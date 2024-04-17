import pika
import os

# Connect to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare a queue
channel.queue_declare(queue='xml_queue', durable=True)

# Get a list of all files in the current directory
files = os.listdir()

# Process each XML file
for file in files:
    if file.endswith('.xml'):
        # Read the XML file
        with open(file, 'r') as f:
            xml_content = f.read()

        # Publish the XML content to the queue
        channel.basic_publish(exchange='', routing_key='xml_queue', body=xml_content)

        print(f"{file} sent to RabbitMQ")

# Close connection
connection.close()