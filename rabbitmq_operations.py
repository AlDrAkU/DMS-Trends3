# Class that contains all the operations that can be performed on RabbitMQ
#
import pika
import secrets
import json
from flask import jsonify
from utils import build_response_message, map_to_json
from data_access.models import InvoiceItem, InvoiceSummary, InvoiceModel, EarningItem, DeductionItem, PaycheckModel, docTypeModel

class RabbitMQOperations:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                "localhost", 5672, "/", pika.PlainCredentials("admin", "admin")
            )
        )
        self.channel = self.connection.channel()

    def queue(self, xml_data):

        correlation_id = secrets.token_hex(4)

        # Declare a queue
        self.channel.queue_declare(queue="xml_queue")
        self.channel.basic_publish(exchange="", routing_key="xml_queue", body=xml_data)
        self.channel.queue_declare(queue="status_queue")
        status_message = build_response_message(
            correlation_id, "XML queued successfully", "no error message"
        )

        # Publish the status message to the status_queue
        self.channel.basic_publish(
            exchange="", routing_key="status_queue", body=json.dumps(status_message)
        )

        self.connection.close()
        # return a json response conatint the correlation_id and the status
        return jsonify({"status": "XML queued successfully", "correlation_id": correlation_id}), 200

    # def dequeue(self):
    #     # Your dequeue logic here