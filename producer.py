import pika
import sys
import time

rabbitmq_service_name = "my-rabbitmq"
rabbitmq_namespace = "default"
rabbitmq_port = 5672

def send_messages(file_path):
    # Set up the credentials and connection parameters
    credentials = pika.PlainCredentials('corti', 'corti')
    parameters = pika.ConnectionParameters(
        host=f"{rabbitmq_service_name}.{rabbitmq_namespace}.svc.cluster.local",
        port=rabbitmq_port,
        credentials=credentials
    )
    
    # Establish the connection
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Make sure the 'logs' queue is declared
    channel.queue_declare(queue='logs', durable=True)
    
    # Continuously send messages
    while True:
        # Re-open the file in each iteration to read contents again
        with open(file_path, 'r') as file:
            for line in file:
                channel.basic_publish(
                    exchange='',
                    routing_key='logs',
                    body=line,
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                print(" [x] Sent %r" % line)
        
        # Wait for a specified time interval (e.g., 60 seconds) before sending the messages again
        time.sleep(1)
    
    # Note: The connection close statement is never reached in this setup; you would need to handle it appropriately if you ever want to exit cleanly.

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        send_messages(file_path)
    else:
        print("Usage: python script.py <file_path>")
