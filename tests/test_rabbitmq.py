import sys
import os
import unittest
import xml.etree.ElementTree as ET

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from flask import json
from app import app as flask_app


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

    def load_xml(self, xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        return ET.tostring(root, encoding="utf-8").decode("utf-8")

    def test_queue_post(self):
        response = self.client.post(
            "/queue", data=self.xml_invoice, content_type="text/json"
        )
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["status"] == f"XML queued successfully"

    def test_dequeue_get(self):
        # Send a GET request to the /dequeue endpoint
        response = self.client.get("/dequeue")
        # Check that the response status code is 200
        assert response.status_code == 200
        response_data = json.loads(response.data)
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
        # Send a GET request to the /dequeue endpoint
        response = self.client.get("/dequeue")
        # Check that the response status code is 200
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data == {'status': 'No more messages in the queue'}

    def test_dequeue_incomplete_file(self):
        # Send a GET request to the /dequeue endpoint
        self.client.post(
            "/queue", data=self.xml_incomplete_paycheck, content_type="text/json"
        )
        response = self.client.get("/dequeue")
        response_data = json.loads(response.data)
        assert response.status_code == 400
        assert response_data == {'error': 'Failed to parse XML: 2 validation errors for DeductionItem\ndescription\n  Field required [type=missing, input_value={}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.7/v/missing\namount\n  Field required [type=missing, input_value={}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.7/v/missing'}

