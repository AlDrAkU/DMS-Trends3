from flask import Flask, request, jsonify
from flasgger import Swagger
import pika
import json
from utils import build_response_message, map_to_json
import secrets
import xml.etree.ElementTree as ET
from data_access.models import docTypeModel, InvoiceModel, PaycheckModel, EarningItem, DeductionItem, InvoiceItem, InvoiceSummary
app = Flask(__name__)
swagger = Swagger(app)


@app.route("/queue", methods=["POST"])
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
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            "localhost", 5672, "/", pika.PlainCredentials("admin", "admin")
        )
    )

    correlation_id = secrets.token_hex(4)
    channel = connection.channel()

    # Declare a queue
    channel.queue_declare(queue="xml_queue")
    channel.basic_publish(exchange="", routing_key="xml_queue", body=xml_data)
    channel.queue_declare(queue="status_queue")
    status_message = build_response_message(
        correlation_id, "XML queued successfully", "no error message"
    )

    # Publish the status message to the status_queue
    channel.basic_publish(
        exchange="", routing_key="status_queue", body=json.dumps(status_message)
    )

    connection.close()

    return jsonify({"status": f"XML {correlation_id} queued successfully"}), 200


@app.route("/dequeue", methods=["GET"])
def dequeue():
    """
    Dequeue XML from RabbitMQ
    ---
    responses:
      200:
        description: XML dequeued successfully
    """
    # Set up a connection to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            "localhost", 5672, "/", pika.PlainCredentials("admin", "admin")
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue="xml_queue")
    # add message to response que
    # Get the next message from the queue
    method_frame, header_frame, body = channel.basic_get("xml_queue")

    if method_frame:
        # Acknowledge the message
        channel.basic_ack(method_frame.delivery_tag)

        channel.queue_declare(queue="status_queue")

        data = map_to_json(body)

        # Load the dictionary into the Pydantic model
        try:
            doc_type = data.get("documentType")
            if doc_type == "INV-01":
                invoice_items_data = data.get("items", {})
                invoice_summary_data = data.get("summary", {})

                # Parse invoice items
                item_data = invoice_items_data.get('item', {})
                invoice_item = InvoiceItem(
                    description=item_data.get('description'),
                    size=item_data.get('size'),
                    finish=item_data.get('finish'),
                    quantity=int(item_data.get('quantity')),
                    unitPrice=float(item_data.get('unitPrice')),
                    total=float(item_data.get('total'))
                )

                # Parse invoice summary
                invoice_summary = InvoiceSummary(
                    subTotal=float(invoice_summary_data.get('subTotal')),
                    discount=float(invoice_summary_data.get('discount')),
                    totalLessDiscount=float(invoice_summary_data.get('totalLessDiscount')),
                    taxRate=float(invoice_summary_data.get('taxRate')),
                    totalTax=float(invoice_summary_data.get('totalTax')),
                    balanceDue=float(invoice_summary_data.get('balanceDue'))
                )

                doc_model = InvoiceModel(
                    documentType=data.get('documentType'),
                    companyName=data.get('header', {}).get('companyName'),
                    address=data.get('header', {}).get('address'),
                    website=data.get('header', {}).get('website'),
                    phone=data.get('header', {}).get('phone'),
                    name=data.get('billTo', {}).get('name'),
                    billToAddress=data.get('billTo', {}).get('address'),
                    email=data.get('billTo', {}).get('email'),
                    billToPhone=data.get('billTo', {}).get('phone'),
                    number=int(data.get('invoiceInfo', {}).get('number')),
                    date=data.get('invoiceInfo', {}).get('date'),
                    dueDate=data.get('invoiceInfo', {}).get('dueDate'),
                    items=[invoice_item],
                    summary=invoice_summary,
                    instruction=data.get('termsAndInstructions', {}).get('instruction'),
                    warranty=data.get('termsAndInstructions', {}).get('warranty')
                )



            elif doc_type == "Pay-01":
                earnings_data = data.get('earnings', {})
                deductions_data = data.get('deductions', {})

                # Parse earnings
                earnings = EarningItem(**earnings_data.get('basicSalary', {}))

                # Parse deductions
                deductions = DeductionItem(**deductions_data.get('tax', {}))

                # fill in  the paycheck pydantic model with the values
                doc_model = PaycheckModel(
                    documentType=data.get('documentType'),
                    title=data.get('header', {}).get('title'),
                    periodStart=data.get('header', {}).get('periodStart'),
                    periodEnd=data.get('header', {}).get('periodEnd'),
                    processingDate=data.get('header', {}).get('processingDate'),
                    name=data.get('employeeInformation', {}).get('name'),
                    position=data.get('employeeInformation', {}).get('position'),
                    department=data.get('employeeInformation', {}).get('department'),
                    earnings=earnings,
                    deductions=deductions,
                    netPay=float(data.get('netPay')),
                    companyName=data.get('employerInformation', {}).get('companyName'),
                    address=data.get('employerInformation', {}).get('address')
                )

            else:
                doc_model = docTypeModel(**data)
            
        except Exception as e:
            connection.close()
            return jsonify({"error": "Failed to parse XML: {}".format(str(e))}), 400

        correlation_id = secrets.token_hex(4)

        # Publish the status message to the status_queue
        channel.queue_declare(queue="status_queue")
        status_message = build_response_message(
            correlation_id, "XML dequeued successfully", doc_model.dict()
        )
        channel.basic_publish(
            exchange="", routing_key="status_queue", body=json.dumps(status_message)
        )

        connection.close()
        return jsonify(doc_model.model_dump()), 200
    else:
        connection.close()
        return jsonify({"status": "No more messages in the queue"}), 200



@app.route("/store", methods=["POST"])
def store():
    """
    Store XML in a database
    ---
    responses:
      200:
        description: XML stored successfully
    """
    # get xml from queue
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            "localhost", 5672, "/", pika.PlainCredentials("admin", "admin")
        )
    )

    # validation

    # saving document to storage

    # saving document uuid, name and timestamp and status to db

    # post status update to status queue

    return jsonify({"status": "XML stored successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
