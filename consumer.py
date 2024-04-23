import pika
import sys
import time

rabbitmq_service_name = "my-rabbitmq"
rabbitmq_namespace = "default"
rabbitmq_port = 5672

def receive_messages(output_file):
    while True:
        try:
            # Set up the credentials and connection parameters
            credentials = pika.PlainCredentials('corti', 'corti')
            parameters = pika.ConnectionParameters(
                host=f"{rabbitmq_service_name}.{rabbitmq_namespace}.svc.cluster.local",
                port=rabbitmq_port,
                credentials=credentials,
                heartbeat=600,  # Configure heartbeat timeout to ensure connection is alive
                blocked_connection_timeout=300  # Timeout for blocked connection (e.g., RabbitMQ is overloaded)
            )
            
            # Establish the connection
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # Ensure the 'logs' queue is declared
            channel.queue_declare(queue='logs', durable=True)

            # Set up the consumer quality of service
            channel.basic_qos(prefetch_count=1)

            # Define the callback function for processing received messages
            def callback(ch, method, properties, body):
                with open(output_file, 'a') as file:
                    message = body.decode()
                    file.write(message + '\n')  # Write each message on a new line
                    print(" [x] Received %r" % message)

            # Setup the consumption on the correct queue name
            channel.basic_consume(queue='logs', on_message_callback=callback, auto_ack=True)

            # Start consuming messages
            print(' [*] Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError:
            print("Connection was closed, retrying...")
            time.sleep(10)  # Wait before retrying to reconnect
        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Exit loop on unexpected errors

if __name__ == "__main__":
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        receive_messages(output_file)
    else:
        print("Usage: python script.py <output_file>")
