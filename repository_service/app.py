from flask import Flask, request
from flasgger import Swagger
from flask_cors import CORS
from utils import utils
from utils.rabbitmq_operations import RabbitMQOperations
from utils.data_access.models import FileModel
from utils.template_operations import TemplateOperations

app = Flask(__name__)
CORS(app)
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Repository Service",
        "version": "0.0.2"
    }
})
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
    # Parse the request data into a FileModel instance
    file_model = FileModel.model_validate(request.get_json())
    xml_data = file_model.data
    storage_type = file_model.storage_type

    return rabbitmq.store(xml_data, storage_type)

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

@app.route("/temporary_file_cleanup", methods=["DELETE"])
def cleanup():
    """ Cleanup temporary files
    ---
    responses:
      204:
        description: Temporary files cleaned up successfully
    """
    return utils.delete_temporary_files()

@app.route("/fetch_all", methods=["GET"])
def fetchAll():
    """ Fetch all the rows from the database
    ---
    responses:
      200:
        description: All rows fetched successfully
    """
    return template.viewFilesTemplate_All()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)