#!/usr/bin/env python3

"""
A standalone script to create exchanges and queues on RabbitMQ for the deal confirmation system.
"""

import pika
import os

# Configuration
amqp_host = os.environ.get('RABBITMQ_HOST') or "localhost"
amqp_port = int(os.environ.get('RABBITMQ_PORT') or 5672)
exchange_name = "deal_events"  # Changed to match the confirm_deal.py
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

    return channel, connection


def create_queue(channel, exchange_name, queue_name, routing_key):
    print(f"Bind to queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)
    # 'durable' makes the queue survive broker restarts

    # bind the queue to the exchange via the routing_key
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )


# Create exchange
channel, connection = create_exchange(
    hostname=amqp_host,
    port=amqp_port,
    exchange_name=exchange_name,
    exchange_type=exchange_type,
)

# Create queues for the deal confirmation system
create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="deal_confirmation_queue",
    routing_key="deal.confirmed",
)

create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="payment_events_queue",
    routing_key="deal.payment_released",
)

create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="notification_queue",
    routing_key="deal.#",  # Subscribe to all deal-related events
)

# Keep the original error and activity log queues
create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="Error",
    routing_key="*.error",
)

create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="Activity_Log",
    routing_key="#",
)

# Close the connection
connection.close()
print("AMQP setup completed.")

if __name__ == '__main__':
    print("AMQP exchange and queues have been created.")