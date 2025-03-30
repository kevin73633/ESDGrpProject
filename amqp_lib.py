"""
Reusable AMQP-related functions

References:
https://pika.readthedocs.io/en/stable/_modules/pika/exceptions.html#ConnectionClosed
"""

import time
import pika
import json
from os import environ


def connect(hostname=None, port=None, exchange_name=None, exchange_type=None, max_retries=12, retry_interval=5):
    """
    Connect to RabbitMQ broker and return connection and channel
    
    Args:
        hostname: RabbitMQ host (default from env or "localhost")
        port: RabbitMQ port (default from env or 5672)
        exchange_name: Name of exchange (default from env or "deal_events")
        exchange_type: Type of exchange (default from env or "topic")
        max_retries: Maximum number of connection attempts
        retry_interval: Seconds between retry attempts
    """
    # Use environment variables if parameters not provided
    hostname = hostname or environ.get('RABBITMQ_HOST') or "localhost"
    port = port or int(environ.get('RABBITMQ_PORT') or 5672)
    exchange_name = exchange_name or environ.get('RABBITMQ_EXCHANGE') or "deal_events"
    exchange_type = exchange_type or environ.get('RABBITMQ_EXCHANGE_TYPE') or "topic"
    
    retries = 0

    # loop to retry connection up to max_retries times
    while retries < max_retries:
        retries += 1
        try:
            print(f"Connecting to AMQP broker {hostname}:{port}...")
            # connect to the broker
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=hostname,
                    port=port,
                    heartbeat=300,
                    blocked_connection_timeout=300,
                )
            )
            print("Connected")

            print("Open channel")
            channel = connection.channel()

            # Check whether the exchange exists
            print(f"Check existence of exchange: {exchange_name}")
            channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_type,
                passive=False,
                durable=True
            )
            # passive=True: If exchange does not exist, raise an error.

            print("Connected")
            return connection, channel

        except pika.exceptions.ChannelClosedByBroker as exception:
            message = f"{exchange_type} exchange {exchange_name} not found."
            connection.close()
            raise Exception(message) from exception

        except pika.exceptions.AMQPConnectionError as exception:
            print(f"Failed to connect: {exception}")
            print(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)

    raise Exception(f"Max {max_retries} retries exceeded...")


def close(connection, channel):
    """Close AMQP channel and connection"""
    if channel and channel.is_open:
        channel.close()
    if connection and connection.is_open:
        connection.close()


def is_connection_open(connection):
    """Check if AMQP connection is still open"""
    try:
        connection.process_data_events()
        return True     
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        return False


def publish_message(routing_key, message, exchange_name=None, hostname=None, port=None, exchange_type=None):
    """
    Publish a message to the AMQP exchange
    
    Args:
        routing_key: Routing key for message
        message: Message payload (will be converted to JSON)
        exchange_name: Name of exchange (default from env)
        hostname: RabbitMQ host (default from env)
        port: RabbitMQ port (default from env)
    """
    try:
        connection, channel = connect(
            hostname=hostname,
            port=port,
            exchange_name=exchange_name,
            exchange_type=exchange_type
        )
        
        # Convert message to JSON if it's a dict
        if isinstance(message, dict):
            message = json.dumps(message)
            
        channel.basic_publish(
            exchange=exchange_name or environ.get('RABBITMQ_EXCHANGE') or "deal_events",
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )
        
        close(connection, channel)
        return True
    except Exception as e:
        print(f"Error publishing message: {str(e)}")
        return False


def start_consuming(
    hostname=None, port=None, exchange_name=None, exchange_type=None, queue_name=None, callback=None
):
    """
    Start consuming messages from a queue
    
    Args:
        hostname: RabbitMQ host (default from env)
        port: RabbitMQ port (default from env)
        exchange_name: Name of exchange (default from env)
        exchange_type: Type of exchange (default from env)
        queue_name: Name of queue to consume from
        callback: Function to call when message is received
    """
    # Use environment variables if parameters not provided
    queue_name = queue_name or environ.get('RABBITMQ_QUEUE')
    
    if not queue_name:
        raise ValueError("Queue name must be provided")
    
    if not callback:
        raise ValueError("Callback function must be provided")
    
    while True:
        try:
            connection, channel = connect(
                hostname=hostname,
                port=port,
                exchange_name=exchange_name,
                exchange_type=exchange_type,
            )

            print(f"Consuming from queue: {queue_name}")
            channel.basic_consume(
                queue=queue_name, on_message_callback=callback, auto_ack=True
            )
            channel.start_consuming()

        except pika.exceptions.ChannelClosedByBroker as exception:
            message = f"Queue {queue_name} not found."
            connection.close()
            raise Exception(message) from exception

        except pika.exceptions.ConnectionClosedByBroker:
            print("Connection closed. Try to reconnect...")
            continue

        except KeyboardInterrupt:
            close(connection, channel)
            break

        # Other types of exception are passed on to caller to handle.
        # Most likely, system issue - RabbitMQ host overload.


def create_notification_consumer(callback, queue_name="notification_queue"):
    """
    Helper function to start a notification consumer
    
    Args:
        callback: Function to call when notification message is received
        queue_name: Name of queue to consume from (default: notification_queue)
    """
    start_consuming(
        queue_name=queue_name,
        callback=callback
    )