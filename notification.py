import pika
import json

rabbit_host = "localhost"
notification_exchange = "notification_topic"
queue_name = "confirm_deal_notification"
routing_key = "notif.confirm_deal"

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
channel = connection.channel()

# Declare exchange
channel.exchange_declare(exchange=notification_exchange, exchange_type="topic", durable=True)

# Declare queue and bind it
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=notification_exchange, queue=queue_name, routing_key=routing_key)

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f"[x] Received: {message}")

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("[*] Waiting for messages. To exit, press CTRL+C")
channel.start_consuming()
