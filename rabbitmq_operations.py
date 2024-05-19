# Class that contains all the operations that can be performed on RabbitMQ
#
import pika
import secrets
import json
from datetime import datetime
import os
from flask import Flask, jsonify
from database.PostgresDatabase import PostgreSQLFileStorageRepository
from utils import build_response_message, map_to_json
from data_access.models import InvoiceItem, InvoiceSummary, InvoiceModel, EarningItem, DeductionItem, PaycheckModel, docTypeModel,FileModel

app = Flask(__name__)

#region RabbitMQ Connection Configuration
# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the config.json file
config_path = os.path.join(script_dir, 'config.json')

# Load the configuration
with open(config_path) as config_file:
    config = json.load(config_file)

# Get the RabbitMQ settings
rabbitmq_config = config['rabbitmq']

# Get the RabbitMQ credentials and parameters
credentials = pika.PlainCredentials(rabbitmq_config['username'], rabbitmq_config['password'])
parameters = pika.ConnectionParameters(rabbitmq_config['host'], rabbitmq_config['port'], rabbitmq_config['vhost'], credentials)

# Get the consumer settings
consumer_enabled = config['rabbitmq']['consumer_enabled']

#endregion

class RabbitMQOperations:
    def __init__(self):
        self.connection = None
        self.channel = None

    def open_connection(self):
        self.connection = pika.BlockingConnection(parameters)
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
            model_dump = RabbitMQOperations.consume_dequeue(method_frame, body, self.channel)
            # Acknowledge the message                
            self.channel.basic_ack(method_frame.delivery_tag)
        else:
            model_dump = jsonify({"status": "No more messages in the queue"}), 200
        self.close_connection()

        return model_dump

        
    def store(self, xml_data, storage_type):
        self.open_connection()

        response = RabbitMQOperations.consume_store(xml_data, storage_type, self.channel)

        self.close_connection()

        return response

        # # Now you can access the data and storage_type fields
        # correlation_id = secrets.token_hex(4)
        # dir_path = f'./data/storage/{storage_type}/{datetime.today().date()}'
        # if not os.path.exists(dir_path):
        #     os.makedirs(dir_path)
        # file_path = f'{dir_path}/{correlation_id}.json'
        # with open(file_path, 'w') as f:
        #     if type(xml_data) == InvoiceModel:
        #         json.dump(xml_data.to_dict(), f)
        #         doctype = "Invoice"
        #     elif type(xml_data) == PaycheckModel:
        #         json.dump(xml_data.to_dict(), f)
        #         doctype = "Paycheck"
        # # saving document uuid, name and timestamp and status to db
        # timestamp = datetime.now()
        # if storage_type == "temp":
        #     temporperm = "Temporary"
        # elif storage_type == "perm":
        #     temporperm = "Permanent"
        # PostgreSQLFileStorageRepository().insert(correlation_id, dir_path,timestamp, doctype, temporperm, "Active")

        # self.channel.queue_declare(queue="status_queue")
        # status_message = build_response_message(
        #         correlation_id, f"XML {correlation_id} stored successfully", "no error message")
        # self.channel.basic_publish(
        #         exchange="", routing_key="status_queue", body=json.dumps(status_message)
        #     )

        # self.close_connection()
        # return jsonify({"status": "XML stored successfully", "uuid":file_path, "correlation_id":correlation_id}), 200
    
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
        
    def consume_dequeue(method_frame, body, channel):    

            channel.queue_declare(queue="status_queue")

            data = map_to_json(body)

            correlation_id = secrets.token_hex(4)

            # Load the dictionary into the Pydantic model
            try:
                doc_type = data.get("documentType")
                if doc_type == "INV-01":
                    invoice_items_data = data.get("items", {})
                    invoice_summary_data = data.get("summary", {})
                    invoice_items = []
                    # Parse invoice items
                    if isinstance(invoice_items_data, list):  # Multiple items
                        for item in invoice_items_data:
                            invoice_item = InvoiceItem(
                                description=item.get('description'),
                                size=item.get('size'),
                                finish=item.get('finish'),
                                quantity=int(item.get('quantity')),
                                unitPrice=float(item.get('unitPrice')),
                                total=float(item.get('total'))
                            )
                            invoice_items.append(invoice_item)

                    else:  # Single item
                        invoice_item = InvoiceItem(
                            description=invoice_items_data.get('description'),
                            size=invoice_items_data.get('size'),
                            finish=invoice_items_data.get('finish'),
                            quantity=int(invoice_items_data.get('quantity')),
                            unitPrice=float(invoice_items_data.get('unitPrice')),
                            total=float(invoice_items_data.get('total'))
                        )
                        invoice_items.append(invoice_item)
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
                        items=invoice_items,
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
                channel.queue_declare(queue="status_queue")
                status_message = build_response_message(
                    correlation_id, {"error": "Failed to parse XML: {}".format(str(e))},body.decode()
                )
                channel.basic_publish(
                    exchange="", routing_key="status_queue", body=json.dumps(status_message)
                )
                with app.app_context():
                    return jsonify({"error": "Failed to parse XML: {}".format(str(e))}), 400


            # Publish the status message to the status_queue
            channel.queue_declare(queue="status_queue")
            status_message = build_response_message(
                correlation_id, "XML dequeued successfully", doc_model.model_dump()
            )
            channel.basic_publish(
                exchange="", routing_key="status_queue", body=json.dumps(status_message)
            )

            with app.app_context():
                return jsonify(doc_model.model_dump()), 200
    
    def consume_store( xml_data, storage_type, channel):
        # Now you can access the data and storage_type fields
        correlation_id = secrets.token_hex(4)
        dir_path = f'./data/storage/{storage_type}/{datetime.today().date()}'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_path = f'{dir_path}/{correlation_id}.json'
        with open(file_path, 'w') as f:
            if type(xml_data) == InvoiceModel:
                json.dump(xml_data.to_dict(), f)
                doctype = "Invoice"
            elif type(xml_data) == PaycheckModel:
                json.dump(xml_data.to_dict(), f)
                doctype = "Paycheck"
        # saving document uuid, name and timestamp and status to db
        timestamp = datetime.now()
        if storage_type == "temp":
            temporperm = "Temporary"
        elif storage_type == "perm":
            temporperm = "Permanent"
        PostgreSQLFileStorageRepository().insert(correlation_id, dir_path,timestamp, doctype, temporperm, "Active")

        channel.queue_declare(queue="status_queue")
        status_message = build_response_message(
                correlation_id, f"XML {correlation_id} stored successfully", "no error message")
        channel.basic_publish(
                exchange="", routing_key="status_queue", body=json.dumps(status_message)
            )
        with app.app_context():
            return jsonify({"status": "XML stored successfully", "uuid":file_path, "correlation_id":correlation_id}), 200
        
    
    def start_consumer():
        def callback(ch, method_frame, properties, body):
            # dequeues the message and stores it in the database
            model_dump = RabbitMQOperations.consume_dequeue(method_frame, body, ch)

            if model_dump[1] == 200:
                # alterations to fit the file model
                model_data = model_dump[0].get_data()
                model_data_json = {"data" : json.loads(model_data.decode("utf-8"))}
                file_model = FileModel.model_validate(model_data_json)
    
                xml_data = file_model.data
                storage_type = file_model.storage_type
                
                # if the data is not a PaycheckModel or InvoiceModel, then do not store it
                if type(xml_data) == InvoiceModel or type(xml_data) == PaycheckModel:
                    # Store the data
                    RabbitMQOperations.consume_store(xml_data, storage_type, ch)

            # Send a delivery acknowledgement
            ch.basic_ack(delivery_tag=method_frame.delivery_tag)

        
        # Connect to the RabbitMQ server
        connection = pika.BlockingConnection(parameters)

        # Create a channel
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue='xml_queue')

        # Set the prefetch count to 1
        channel.basic_qos(prefetch_count=1)

        # Start consuming messages
        channel.basic_consume(queue='xml_queue', on_message_callback=callback)

        # Start consuming messages
        channel.start_consuming()