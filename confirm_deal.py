from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pika
import sys, os

import amqp_lib
from invokes import invoke_http

app = Flask(__name__)

CORS(app)

user_URL = "http://localhost:5001/user"

# RabbitMQ
rabbit_host = "localhost"
rabbit_port = 5672
notification_exchange = "notification_topic" 
error_exchange = "error_topic"
exchange_type = "topic"

# queue name for this composite service:     "confirm_deal_notification"
# routing key for this composite service:     "notif.confirm_deal"

connection = None 
channel = None

def connectAMQP():
    # Use global variables to reduce number of reconnection to RabbitMQ
    # There are better ways but this suffices for our lab
    global connection
    global channel

    print("  Connecting to AMQP broker...")
    try:
        connection, channel = amqp_lib.connect(
                hostname=rabbit_host,
                port=rabbit_port,
                exchange_name=notification_exchange,
                exchange_type=exchange_type,
                
        )
        
        ##################################
        channel.exchange_declare(
            exchange=notification_exchange, 
            exchange_type="topic", 
            durable=True
            )
        
        channel.exchange_declare(
            exchange=error_exchange, 
            exchange_type="topic", 
            durable=True
            )
        ###################################
        
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
        exit(1) # terminate


@app.route("/confirm_deal", methods=["POST"])
def confirm_deal():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            # when receiving deal confirmation request from the ui
            deal = request.get_json()  # Get things like buyer id and seller id from data from request
            print("\nReceived a deal confirmation in JSON:", deal)  
                
            result = processGetAllUsers(deal)
            
            if isinstance(result, tuple):
                result, status_code = result
            elif not isinstance(result, dict):
                return jsonify({"code": 500, "message": "Unexpected response type"}), 500

            return jsonify(result), result["code"]
            
            
            
        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print("Error: {}".format(ex_str))

            return jsonify(
                    {
                        "code": 500,
                        "message": "confirm_deal.py internal error:",
                        "exception": ex_str,
                    }
            ), 500
            
    # if reached here, not a JSON request.
    return jsonify(
        {"code": 400, "message": "Invalid JSON input: " + str(request.get_data())}
    ), 400


######### this function is incomplete, just edited it to test amqp
def processGetAllUsers(deal):
    if connection is None or not amqp_lib.is_connection_open(connection):
        connectAMQP()
        
    buyer_id = deal.get("buyerID")
    if not buyer_id:
        return {"code": 400, "message": "Missing buyerID."}
        
    # when retrieving buyer payment details from user 
    print("Invoking user microservice to get buyer payment details...")
    user_result = invoke_http(f"{user_URL}/getAccNumFromUser/{buyer_id}", method="GET")
    
    # Ensure it's a dictionary, not a Response object
    if not isinstance(user_result, dict):
        try:
            user_result = user_result.json()  # Convert Flask Response to dict
        except AttributeError:
            return {
                "code": 500,
                "message": "Error processing user microservice response.",
                "data": str(user_result),
            }
    
    print(f"User microservice result: {user_result}")

    message = json.dumps(user_result)

    code = user_result["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        print("  Publish message with routing_key=deal.error\n")
        channel.basic_publish(
                exchange=error_exchange,
                routing_key="deal.error",
                body=message,
                properties=pika.BasicProperties(delivery_mode=2),
        )
        # make message persistent within the matching queues until it is received by some receiver
        # (the matching queues have to exist and be durable and bound to the exchange)

        # 7. Return error
        return {
            "code": 500,
            "data": {"user_result": user_result},
            "message": "buyer payment detail retrieval failure sent for error handling.",
        }
    
    print("  Publish message with routing_key=notif.confirm_deal\n")
    channel.basic_publish(
        exchange="notification_topic", routing_key="notif.confirm_deal", body=message
    )

    buyer_payment_details = user_result["data"].get("AccNum")

    return {
        "code": 200,
        "message": "Buyer payment details retrieved successfully.",
        "buyer_payment_details": buyer_payment_details
    }

    
    


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("Starting confirm_deal service...")
    connectAMQP()
    app.run(host="0.0.0.0", port=5100, debug=True)




############ code for the entire user scenario 1??????

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import json
# import pika
# import sys, os

# import amqp_lib
# from invokes import invoke_http

# app = Flask(__name__)
# CORS(app)

# # URLs for microservices
# user_URL = "http://localhost:5001/user"
# deal_URL = "http://localhost:5003/deal"
# payment_URL = "http://localhost:5004/payment"
# payment_record_URL = "http://localhost:5005/payment_record"

# # RabbitMQ
# rabbit_host = "localhost"
# rabbit_port = 5672
# notification_exchange = "notification_topic" 
# error_exchange = "error_topic"
# exchange_type = "topic"

# connection = None 
# channel = None

# def connectAMQP():
#     global connection
#     global channel

#     print("Connecting to AMQP broker...")
#     try:
#         connection, channel = amqp_lib.connect(
#             hostname=rabbit_host,
#             port=rabbit_port,
#             exchange_name=notification_exchange,
#             exchange_type=exchange_type,
#         )
#         channel.exchange_declare(exchange=notification_exchange, exchange_type="topic", durable=True)
#         channel.exchange_declare(exchange=error_exchange, exchange_type="topic", durable=True)
#     except Exception as e:
#         print(f"Unable to connect to RabbitMQ: {e}")
#         exit(1)

# @app.route("/confirm_deal", methods=["POST"])
# def confirm_deal():
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"code": 400, "message": "Invalid JSON input"}), 400

#         deal_id = data.get("dealID")
#         buyer_id = data.get("buyerID")
#         seller_id = data.get("sellerID")

#         # Step 2-3: Get deal details
#         deal_result = invoke_http(f"{deal_URL}/{deal_id}", method="GET")
#         if deal_result["code"] != 200:
#             return jsonify(deal_result), deal_result["code"]
#         price = deal_result["data"]["price"]

#         # Step 4-5: Retrieve buyer payment details
#         user_result = invoke_http(f"{user_URL}/{buyer_id}/payment", method="GET")
#         if user_result["code"] != 200:
#             return jsonify(user_result), user_result["code"]
#         payment_details = user_result["data"]

#         # Step 6-7: Make payment
#         payment_payload = {
#             "buyerID": buyer_id,
#             "sellerID": seller_id,
#             "price": price,
#             "description": "Payment for deal",
#             "stripeAccountID": payment_details["stripeAccountID"],
#             "paymentMethodID": payment_details["paymentMethodID"]
#         }
#         payment_result = invoke_http(payment_URL, method="POST", json=payment_payload)
#         if payment_result["code"] != 200:
#             return jsonify(payment_result), payment_result["code"]

#         # Step 8: Log payment record
#         record_payload = {**payment_payload, "status": "Success"}
#         record_result = invoke_http(payment_record_URL, method="POST", json=record_payload)
#         if record_result["code"] != 201:
#             return jsonify(record_result), record_result["code"]

#         # Step 9: Update deal status
#         update_payload = {"status": "Completed"}
#         update_result = invoke_http(f"{deal_URL}/{deal_id}", method="POST", json=update_payload)
#         if update_result["code"] != 200:
#             return jsonify(update_result), update_result["code"]

#         # Step 10: Send notification
#         notification_message = json.dumps({
#             "buyerID": buyer_id,
#             "sellerID": seller_id,
#             "price": price
#         })
#         channel.basic_publish(
#             exchange=notification_exchange,
#             routing_key="notif.confirm_deal",
#             body=notification_message,
#             properties=pika.BasicProperties(delivery_mode=2)
#         )

#         return jsonify({"code": 201, "message": "Deal confirmed successfully."}), 201
#     except Exception as e:
#         return jsonify({"code": 500, "message": "Internal server error", "error": str(e)}), 500

# if __name__ == "__main__":
#     print("Starting Confirm Deal service...")
#     app.run(host="0.0.0.0", port=5100, debug=True)