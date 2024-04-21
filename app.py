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

if __name__ == '__main__':
    app.run(debug=True)
