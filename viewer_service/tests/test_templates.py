import unittest
from viewer_service.app import app as flask_app

class TestTemplates(unittest.TestCase):
    def setUp(self):
        self.app = flask_app
        self.client = self.app.test_client()
        self.app.app_context().push()

    def test_get_paycheck_template(self):
        response = self.client.get("/paycheck_template")  # Use the test client to send the request
        with open('expected_paycheck_response.html', 'r') as file:
            expected_response = file.read()
        assert response.status_code == 200
        assert response.data.decode("utf-8") == expected_response

    def test_get_invoice_template(self):
        response = self.client.get("/invoice_template")  # Use the test client to send the request
        with open('expected_invoice_response.html', 'r') as file:
            expected_response = file.read()
        assert response.status_code == 200
        assert response.data.decode("utf-8") == expected_response