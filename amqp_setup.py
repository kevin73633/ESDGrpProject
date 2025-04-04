#!/usr/bin/env python3

"""
A standalone script to create exchanges and queues on RabbitMQ for all user scenarios in the deal system.
"""

import pika
import os
import time
import sys

# Configuration
amqp_host = os.environ.get('RABBITMQ_HOST') or "localhost"
amqp_port = int(os.environ.get('RABBITMQ_PORT') or 5672)
exchange_name = os.environ.get('RABBITMQ_EXCHANGE') or "deal_events"
exchange_type = "topic"
max_retries = 10
retry_interval = 5

def create_exchange_and_queues():
    """Main function to create the exchange and all queues"""
    retries = 0

    while retries < max_retries:
        try:
            print(f"Connecting to AMQP broker {amqp_host}:{amqp_port} (attempt {retries+1}/{max_retries})...")
            # connect to the broker
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=amqp_host,
                    port=amqp_port,
                    heartbeat=300,
                    blocked_connection_timeout=300,
                )
            )
            print("Connected successfully")

            print("Opening channel")
            channel = connection.channel()

            # Set up the exchange if the exchange doesn't exist
            print(f"Declaring exchange: {exchange_name}")
            channel.exchange_declare(
                exchange=exchange_name, exchange_type=exchange_type, durable=True
            )
            # 'durable' makes the exchange survive broker restarts

            # Create ONE queue for EACH scenario:

            # 1. Deal Confirmation Scenario (port 5100)
            create_queue(
                channel=channel,
                exchange_name=exchange_name,
                queue_name="deal_confirmation_queue",
                routing_key="deal.confirmed.#",  # Will catch all deal.confirmed.* events
            )

            # 2. Deal Verification Scenario (port 5200)
            create_queue(
                channel=channel,
                exchange_name=exchange_name,
                queue_name="deal_verification_queue",
                routing_key="deal.verified.#",  # Will catch all deal.verified.* events
            )

            # 3. User Reporting Scenario (port 5300)
            create_queue(
                channel=channel,
                exchange_name=exchange_name,
                queue_name="user_report_queue",
                routing_key="user.reported.#",  # Will catch all user.reported.* events
            )

            # System-wide error and logging queue (optional)
            create_queue(
                channel=channel,
                exchange_name=exchange_name,
                queue_name="error_queue",
                routing_key="*.error",
            )
            
            # Legacy notification queue for compatibility
            create_queue(
                channel=channel,
                exchange_name=exchange_name,
                queue_name="notification_queue",
                routing_key="#",  # Catch all messages
            )

            # Close the connection
            connection.close()
            print("AMQP setup completed successfully!")
            return True
            
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection error: {e}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print(f"Failed to connect after {max_retries} attempts")
                return False
                
        except Exception as e:
            print(f"Error setting up AMQP: {e}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print(f"Failed after {max_retries} attempts")
                return False

def create_queue(channel, exchange_name, queue_name, routing_key):
    """Create a queue and bind it to the exchange with the specified routing key"""
    print(f"Creating queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)
    # 'durable' makes the queue survive broker restarts

    # Bind the queue to the exchange via the routing_key
    print(f"Binding queue: {queue_name} to routing key: {routing_key}")
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )

if __name__ == '__main__':
    print("Starting AMQP setup...")
    success = create_exchange_and_queues()
    if success:
        print("AMQP setup completed successfully.")
        sys.exit(0)
    else:
        print("AMQP setup failed!")
        sys.exit(1)