import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flask import json
from app import app as flask_app 


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_queue_post(client):
    # Define your XML data
    xml_data = "{<root><child>Test</child></root>}"

    # Send a POST request to the /queue endpoint with the XML data
    response = client.post("/queue", data=xml_data, content_type='text/json')

    # Check that the response status code is 200
    assert response.status_code == 200

    # Check that the response message is as expected
    response_data = json.loads(response.data)
    assert response_data["status"] == "XML queued successfully"


def test_dequeue_get(client):
    # Send a GET request to the /dequeue endpoint
    response = client.get("/dequeue")

    # Check that the response status code is 200
    assert response.status_code == 200

    # Check that the response message is as expected

    response_data = json.loads(response.data)
    assert response_data["status"] == "XML dequeued successfully"
    assert response_data["message"] == '{<root><child>Test</child></root>}'