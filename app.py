from flask import Flask, request, jsonify
from flasgger import Swagger
import pika
import json
from utils import build_response_message, map_to_json
import secrets
from datetime import datetime
from data_access.models import docTypeModel, InvoiceModel, PaycheckModel, EarningItem, DeductionItem, InvoiceItem, \
    InvoiceSummary, FileModel
import os
from rabbitmq_operations import RabbitMQOperations

app = Flask(__name__)
swagger = Swagger(app)
rabbitmq = RabbitMQOperations()


@app.route("/queue", methods=["POST"])
def queue():
    """ Queue XML on RabbitMQ
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
        correlation_id: string
    """
    xml_data = request.data
    return rabbitmq.queue(xml_data)


@app.route("/dequeue", methods=["GET"])
def dequeue():
    """ Dequeue XML from RabbitMQ
    ---
    responses:
      200:
        description: XML dequeued successfully
    """
    return rabbitmq.dequeue()
    
@app.route("/store", methods=["POST"])
def store():
    """ Store XML in a database
    ---
    parameters:
      - name: body
        in: body
        required: true
    responses:
      200:
        description: XML stored successfully
    """
    return rabbitmq.store(request)
    
@app.route("/status_dequeue", methods=["GET"])
def statusDequeue():
    """
    Dequeue status message from RabbitMQ
    ---
    responses:
      200:
        description: status dequeued successfully
    """
    # Set up a connection to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            "localhost", 5672, "/", pika.PlainCredentials("admin", "admin")
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue="status_queue")
    # Get the next message from the queue
    method_frame, header_frame, body = channel.basic_get("status_queue")

    if method_frame:
        # Acknowledge the message
        channel.basic_ack(method_frame.delivery_tag)
        connection.close()
        # Return the message
        return jsonify(json.loads(body)), 200
    else:
        connection.close()
        return jsonify({"status": "No more messages in the queue"}), 200
    
def purge_queue(queue_name):
    """
    Purge all the messages in the given queue from RabbitMQ
    """
    # Set up a connection to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            "localhost", 5672, "/", pika.PlainCredentials("admin", "admin")
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    # Purge the queue
    channel.queue_purge(queue=queue_name)
    connection.close()
    return jsonify({"status": "No more messages in the queue"}), 204

@app.route("/purge_status_queue", methods=["DELETE"])
def statusPurge():
    """
    Purge all the messages in the status queue from RabbitMQ
    ---
    responses:
      204:
        description: status queue successfully purged
    """
    return purge_queue("status_queue")

@app.route("/purge_xml_queue", methods=["DELETE"])
def xmlPurge():
    """
    Purge all the messages in the XML queue from RabbitMQ
    ---
    responses:
      204:
        description: XML queue successfully purged
    """
    return purge_queue("xml_queue")

if __name__ == "__main__":
    app.run(debug=True)