import pika
import sys
import time
from prometheus_client import start_http_server, Counter

rabbitmq_service_name = "my-rabbitmq"
rabbitmq_namespace = "default"
rabbitmq_port = 5672

# Define a counter metric for tracking the number of messages processed
messages_processed_counter = Counter('messages_processed_total', 'Total number of processed messages')

def receive_messages(output_file):
    # Prometheus metrics on port 8000
    start_http_server(8000)

    while True:
        try:
            # Creds and Connection (For prod - saved in store key like Hashicorp Vault)
            credentials = pika.PlainCredentials('corti', 'corti')
            parameters = pika.ConnectionParameters(
                host=f"{rabbitmq_service_name}.{rabbitmq_namespace}.svc.cluster.local",
                port=rabbitmq_port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            # Connection
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # Logs Q
            channel.queue_declare(queue='logs', durable=True)

            # Set up the consumer quality of service
            channel.basic_qos(prefetch_count=1)

            # Define the callback function for processing received messages
            def callback(ch, method, properties, body):
                with open(output_file, 'a') as file:
                    message = body.decode()
                    file.write(message + '\n')
                    print(" [x] Received %r" % message)
                    # Increment the messages processed counter for each received message
                    messages_processed_counter.inc()

            # Setup the consumption on the correct queue name
            channel.basic_consume(queue='logs', on_message_callback=callback, auto_ack=True)

            # Start consuming messages
            print(' [*] Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError:
            print("Connection was closed, retrying...")
            time.sleep(10)
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        receive_messages(output_file)
    else:
        print("Usage: python script.py <output_file>")
