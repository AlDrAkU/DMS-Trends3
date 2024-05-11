from flask import Flask, request, jsonify, redirect, url_for
from flasgger import Swagger

import utils
from rabbitmq_operations import RabbitMQOperations
from template_operations import TemplateOperations

app = Flask(__name__)
swagger = Swagger(app)
rabbitmq = RabbitMQOperations()
template = TemplateOperations()


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
    """ Dequeue status message from RabbitMQ
    ---
    responses:
      200:
        description: status dequeued successfully
    """
    return rabbitmq.status_dequeue()

@app.route("/purge_status_queue", methods=["DELETE"])
def statusPurge():
    """ Purge all the messages in the status queue from RabbitMQ
    ---
    responses:
      204:
        description: status queue successfully purged
    """
    return rabbitmq.purge_queue("status_queue")

@app.route("/purge_xml_queue", methods=["DELETE"])
def xmlPurge():
    """ Purge all the messages in the XML queue from RabbitMQ
    ---
    responses:
      204:
        description: XML queue successfully purged
    """
    return rabbitmq.purge_queue("xml_queue")

# Paycheck template
@app.route("/paycheck_template", methods=["GET"])
def paycheckTemplate():
    """ Get the paycheck template
    ---
    responses:
      200:
        description: Paycheck template retrieved successfully
    """
    return template.paycheckTemplate("paycheck.json")

# Invoice template
@app.route("/invoice_template", methods=["GET"])
def invoiceTemplate():
    """ Get the invoice template
    ---
    responses:
      200:
        description: Invoice template retrieved successfully
    """
    return template.invoiceTemplate("invoice.json")

@app.route("/temporary_file_cleanup", methods=["DELETE"])
def cleanup():
    """ Cleanup temporary files
    ---
    responses:
      204:
        description: Temporary files cleaned up successfully
    """
    return utils.delete_temporary_files()
if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)