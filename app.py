from flask import Flask, request, jsonify, redirect, url_for,abort
from flasgger import Swagger
import utils
from rabbitmq_operations import RabbitMQOperations
from template_operations import TemplateOperations
from data_access.models import FileModel

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

# Paycheck template
@app.route("/paycheck_template", methods=["GET"])
def paycheckTemplate():
    """ Get the paycheck template
    ---
    responses:
      200:
        description: Paycheck template retrieved successfully
    """
    return template.paycheckTemplate("2024-05-05/paycheck.json")
@app.route("/paycheck_template/<uuid>", methods=["GET"])
def paycheckTemplateUuid(uuid):
    """ Get the paycheck template
    ---
    parameters:
      - name: uuid
        in: path
        required: true
        type: string
        description: The UUID of the file
    responses:
      200:
        description: Paycheck template retrieved successfully
    """
    return template.paycheckTemplate("2024-05-05/paycheck.json",uuid)
# Invoice template
@app.route("/invoice_template", methods=["GET"])
def invoiceTemplate():
    """ Get the invoice template
    ---
    responses:
      200:
        description: Invoice template retrieved successfully
    """
    return template.invoiceTemplate("2024-05-11/invoice.json")

@app.route("/invoice_template/<uuid>", methods=["GET"])
def invoiceTemplateUuid(uuid):
    """ Get the invoice template filled in with the requested uuid data
    ---
    parameters:
      - name: uuid
        in: path
        required: true
        type: string
        description: The UUID of the file
    responses:
      200:
        description: Invoice template retrieved successfully
    """
    return template.invoiceTemplate("2024-05-11/invoice.json",uuid)

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

@app.route("/fetch_one/<uuid>", methods=["GET"])
def fetchOne(uuid):
    """ Fetch one row from the database
    ---
    parameters:
      - name: uuid
        in: path
        required: true
        type: string
    responses:
      200:
        description: Row fetched successfully
    """
    return template.viewFilesTemplate_Single(uuid)
@app.route("/fetch_file_view/<uuid>/<docType>", methods=["GET"])
def fetchFileView(uuid, docType):
    """ Fetch the file view template and redirect based on DocType
    ---
    parameters:
      - name: uuid
        in: path
        required: true
        type: string
        description: The UUID of the file
      - name: docType
        in: path
        required: true
        type: string
        description: The type of document (invoice or paycheck)
    responses:
      302:
        description: Redirects to the appropriate template
      404:
        description: DocType not found or invalid
    """
    if docType.lower() == 'invoice':
        return redirect(url_for('invoiceTemplateUuid', uuid=uuid))
    elif docType.lower() == 'paycheck':
        return redirect(url_for('paycheckTemplateUuid', uuid=uuid))
    else:
        abort(404)



if __name__ == "__main__":
    app.run(debug=True)