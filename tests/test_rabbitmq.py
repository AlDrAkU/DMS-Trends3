import sys
import os
import unittest
import xml.etree.ElementTree as ET

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from flask import json
from app import app as flask_app
from rabbitmq_operations import RabbitMQOperations


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client



class TestRabbitMQ(unittest.TestCase):
    def setUp(self):
        self.app = flask_app
        self.client = self.app.test_client()
        self.xml_paycheck = self.load_xml("../data/test_documents/paycheck.xml")
        self.xml_invoice = self.load_xml("../data/test_documents/invoice.xml")
        self.xml_incomplete_paycheck = self.load_xml("../data/test_documents/incomplete_paycheck.xml")
        self.rabbitmq = RabbitMQOperations()        
        self.app_context = self.app.app_context()  # Create an application context
        self.app_context.push()  # Push the application context

    def load_xml(self, xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        return ET.tostring(root, encoding="utf-8").decode("utf-8")

    def test_queue_post(self):
        ## setup the test
        # purge the xml queue
        self.rabbitmq.purge_queue(queue_name="xml_queue")

        ## Exercise the code   
        with self.app.test_request_context():
            response = self.rabbitmq.queue(self.xml_invoice)

        ## Assertions
        assert response[1] == 200
        response_data = json.loads(response[0].data)
        assert response_data["status"] == f"XML queued successfully"


    def test_dequeue_get(self):
        ## setup the test
        # purge the xml queue
        self.rabbitmq.purge_queue(queue_name = "xml_queue")
        # queue an xml
        with self.app.test_request_context():
            self.test_queue_post()

        ## Exercise the code
        # Send a GET request to the /dequeue endpoint
        with self.app.test_request_context():
            response = self.rabbitmq.dequeue()

        ## Assertions
        # Check that the response status code is 200
        assert response[1] == 200
        response_data = json.loads(response[0].data)
        assert response_data == {
            "address": "Alfons Gossetlaan 46 1702 Groot-Bijgaarden",
            "billToAddress": "Retail Concepts NV, Smallandlaan 9, 2660 Hoboken",
            "billToPhone": "+32 (0)3 828 30 15",
            "companyName": "Brico",
            "date": "18/04/2024",
            "documentType": "INV-01",
            "dueDate": "30/04/2024",
            "email": "team@asadventure.com",
            "instruction": "Payment Instructions",
            "items": [
                 {
                 'description': 'Ceramic Floor Tile',
                 'finish': 'Glossy',
                 'quantity': 100,
                 'size': '12x12 inches',
                 'total': 150.0,
                 'unitPrice': 1.5,
                },
                {
                    "description": "Porcelain Floor Tile",
                    "finish": "Matte",
                    "quantity": 50,
                    "size": "24x24 inches",
                    "total": 100.0,
                    "unitPrice": 2.0,
                }
            ],
            "name": "AS Adventure",
            "number": 6000001,
            "phone": "0800 12 365",
            "summary": {
                "balanceDue": 270.0,
                "discount": 0.0,
                "subTotal": 250.0,
                "taxRate": 8.0,
                "totalLessDiscount": 250.0,
                "totalTax": 20.0,
            },
            "warranty": "Product Warranty Information",
            "website": "https://www.brico.be/nl/",
        }


    def test_dequeue_get_no_item_in_que(self):
        ## setup the test
        # purge the xml queue
        self.rabbitmq.purge_queue(queue_name="xml_queue")

        ## Exercise the code   
        with self.app.test_request_context():
            response = self.rabbitmq.dequeue()

        # Check that the response status code is 200
        assert response[1] == 200
        response_data = json.loads(response[0].data)
        assert response_data == {'status': 'No more messages in the queue'}

    def test_dequeue_incomplete_file(self):
        ## setup the test
        # purge the xml queue
        self.rabbitmq.purge_queue(queue_name="xml_queue")
        # queue an incomplete xml
        with self.app.test_request_context():
            self.rabbitmq.queue(self.xml_incomplete_paycheck)
        
        ## Execute the code   
        with self.app.test_request_context():
            response = self.rabbitmq.dequeue()
            
        response_data = json.loads(response[0].data)

        assert response[1] == 400
        assert response_data == {'error': 'Failed to parse XML: 2 validation errors for DeductionItem\ndescription\n  Field required [type=missing, input_value={}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.7/v/missing\namount\n  Field required [type=missing, input_value={}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.7/v/missing'}

    def test_queue_post_status_queue(self):
        ## setup the test
        # purge the status queue
        self.rabbitmq.purge_queue(queue_name="status_queue")
        # queue an xml
        with self.app.test_request_context():
            response = self.rabbitmq.queue(self.xml_invoice)
        # Retrieve the correlation_id from the response
        response_data = json.loads(response[0].data)
        correlation_id = response_data["correlation_id"]

        ## Exercise the code
        # Check that the last message in the status_queue contains the correlation_id of the sent message  
        with self.app.test_request_context():
            response = self.rabbitmq.status_dequeue()

        response_data = json.loads(response[0].data)
        assert response_data["correlation_id"] == correlation_id
    
    def tearDown(self):
        self.app_context.pop()  # Pop the application context when the test is done

