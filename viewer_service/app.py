from flask import Flask, redirect, url_for, abort
from flasgger import Swagger
from flask_cors import CORS
from utils.template_operations import TemplateOperations

app = Flask(__name__)
CORS(app)
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Viewer Service",
        "version": "0.0.2"
    }
})
template = TemplateOperations()

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
    return template.paycheckTemplate("2024-05-05/paycheck.json", uuid)

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
    return template.invoiceTemplate("2024-05-11/invoice.json", uuid)

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
    app.run(debug=True, host='0.0.0.0', port=5001)
