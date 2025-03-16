#!/usr/bin/env python3

"""
A standalone script to create exchanges and queues on RabbitMQ.
"""

import pika

amqp_host = "localhost"
amqp_port = 5672
notification_exchange = "notification_topic" #specific to posting notifs
error_exchange = "error_topic" #more for errors across all services 
exchange_type = "topic"


def create_exchange(hostname, port, exchange_name, exchange_type):
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

    # Set up the exchange if the exchange doesn't exist
    print(f"Declare exchange: {exchange_name}")
    channel.exchange_declare(
        exchange=exchange_name, exchange_type=exchange_type, durable=True
    )
    # 'durable' makes the exchange survive broker restarts

    return channel

notification_channel = create_exchange(
    amqp_host, 
    amqp_port, 
    notification_exchange, 
    exchange_type
    )

error_channel = create_exchange(
    amqp_host, 
    amqp_port, 
    error_exchange, 
    exchange_type
    )


def create_queue(channel, exchange_name, queue_name, routing_key):
    print(f"Bind to queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)
    # 'durable' makes the queue survive broker restarts

    # bind the queue to the exchange via the routing_key
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )


create_queue(
    notification_channel, 
    notification_exchange, 
    "confirm_deal_notification", 
    "notif.confirm_deal"
    )

create_queue(
    notification_channel, 
    notification_exchange, 
    "verify_deal_notification", 
    "notif.verify_deal"
    )

create_queue(
    notification_channel, 
    notification_exchange, 
    "report_chat_notification", 
    "notif.report_chat"
    )

create_queue(
    error_channel, 
    error_exchange, 
    "Error", 
    "*.error"
    ) 