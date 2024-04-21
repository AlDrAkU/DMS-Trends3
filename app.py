from flask import Flask, request, jsonify
from flasgger import Swagger
import pika

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/queue', methods=['POST'])
def queue():
    """
    Queue XML on RabbitMQ
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: XMLData
          required:
            - xml
          properties:
            xml:
              type: string
              description: The XML data to be queued
    responses:
      200:
        description: XML queued successfully
    """
    # Get XML data from the request
    xml_data = request.data

    # Set up a connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare a queue
    channel.queue_declare(queue='xml_queue')

    # Publish the XML data to the queue
    channel.basic_publish(exchange='', routing_key='xml_queue', body=xml_data)

    connection.close()

    return jsonify({'status': 'XML queued successfully'}), 200

@app.route('/dequeue', methods=['GET'])
def dequeue():
    """
    Dequeue XML from RabbitMQ
    ---
    responses:
      200:
        description: XML dequeued successfully
    """
    # Set up a connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the same queue
    channel.queue_declare(queue='xml_queue')

    # Get the next message from the queue
    method_frame, header_frame, body = channel.basic_get('xml_queue')

    if method_frame:
        # Acknowledge the message
        channel.basic_ack(method_frame.delivery_tag)
        connection.close()
        return jsonify({'status': 'XML dequeued successfully', 'xml': body.decode()}), 200
    else:
        connection.close()
        return jsonify({'status': 'No more messages in the queue'}), 200

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)
