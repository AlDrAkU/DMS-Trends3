# Class that contains all the operations that can be performed on RabbitMQ
#
import pika
import secrets
import json
from datetime import datetime
import os
from flask import jsonify
from utils import build_response_message, map_to_json
from data_access.models import InvoiceItem, InvoiceSummary, InvoiceModel, EarningItem, DeductionItem, PaycheckModel, docTypeModel, FileModel

class RabbitMQOperations:
    def __init__(self):
        self.connection = None
        self.channel = None

    def open_connection(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                "localhost", 5672, "/", pika.PlainCredentials("admin", "admin")
            )
        )
        self.channel = self.connection.channel()

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.channel = None

    def queue(self, xml_data):
        self.open_connection()

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

        self.close_connection()
        # return a json response conatint the correlation_id and the status
        return jsonify({"status": "XML queued successfully", "correlation_id": correlation_id}), 200

    def dequeue(self):    
        self.open_connection()    
        
        self.channel.queue_declare(queue="xml_queue")
        # add message to response que
        # Get the next message from the queue
        method_frame, header_frame, body = self.channel.basic_get("xml_queue")

        if method_frame:
            # Acknowledge the message
            self.channel.basic_ack(method_frame.delivery_tag)

            self.channel.queue_declare(queue="status_queue")

            data = map_to_json(body)

            correlation_id = secrets.token_hex(4)

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
                # Publish the status message to the status_queue
                self.channel.queue_declare(queue="status_queue")
                status_message = build_response_message(
                    correlation_id, {"error": "Failed to parse XML: {}".format(str(e))},body.decode()
                )
                self.channel.basic_publish(
                    exchange="", routing_key="status_queue", body=json.dumps(status_message)
                )
                self.connection.close()
                return jsonify({"error": "Failed to parse XML: {}".format(str(e))}), 400


            # Publish the status message to the status_queue
            self.channel.queue_declare(queue="status_queue")
            status_message = build_response_message(
                correlation_id, "XML dequeued successfully", doc_model.model_dump()
            )
            self.channel.basic_publish(
                exchange="", routing_key="status_queue", body=json.dumps(status_message)
            )

            self.close_connection()
            return jsonify(doc_model.model_dump()), 200
        else:
            self.close_connection()
            return jsonify({"status": "No more messages in the queue"}), 200
        
    def store(self, request):
        self.open_connection()

        # Parse the request data into a FileModel instance
        file_model = FileModel.model_validate(request.get_json())

        # Now you can access the data and storage_type fields
        xml_data = file_model.data
        storage_type = file_model.storage_type
        correlation_id = secrets.token_hex(4)
        dir_path = f'./data/storage/{storage_type}/{datetime.today().date()}'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_path = f'{dir_path}/{correlation_id}.json'
        with open(file_path, 'w') as f:
            if type(xml_data) == InvoiceModel:
                json.dump(xml_data.to_dict(), f)
            elif type(xml_data) == PaycheckModel:
                json.dump(xml_data.to_dict(), f)
        # TODO: saving document uuid, name and timestamp and status to db

        self.channel.queue_declare(queue="status_queue")
        status_message = build_response_message(
                correlation_id, f"XML {correlation_id} stored successfully", "no error message")
        self.channel.basic_publish(
                exchange="", routing_key="status_queue", body=json.dumps(status_message)
            )

        self.close_connection()
        return jsonify({"status": "XML stored successfully", "uuid":file_path, "correlation_id":correlation_id}), 200
    
    def purge_queue(self, queue_name):
        """
        Purge all the messages in the given queue from RabbitMQ
        """
        self.open_connection()

        self.channel.queue_declare(queue=queue_name)
        # Purge the queue
        self.channel.queue_purge(queue=queue_name)
        self.close_connection()
        return jsonify({"status": "No more messages in the queue"}), 204
    
    def status_dequeue(self):
        """
        Dequeue the status message from the status_queue
        """
        self.open_connection()

        self.channel.queue_declare(queue="status_queue")
        method_frame, header_frame, body = self.channel.basic_get("status_queue")
        if method_frame:
            self.channel.basic_ack(method_frame.delivery_tag)
            self.close_connection()
            return jsonify(json.loads(body)), 200
        else:
            self.close_connection()
            return jsonify({"status": "No more messages in the queue"}), 200