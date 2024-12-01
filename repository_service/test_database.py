#Tests for the Postgres database
import sys
import os
from datetime import datetime
module_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(module_dir)
sys.path.append(parent_dir)

import secrets
import unittest
from utils.database.PostgresDatabase import PostgreSQLFileStorageRepository

class TestPostgresDatabase(unittest.TestCase):
    def setUp(self):
        self.postgres = PostgreSQLFileStorageRepository(postgres_host="localhost")
        self.connection = self.postgres.connect()
        self.cursor = self.connection.cursor()

    def test_insert(self):
        # Test the insert method
        uuid = secrets.token_hex(4)
        now = datetime.now()
        self.postgres.insert(uuid, "test.txt", now, "Invoice", "Permanent", "Active")
        result = self.postgres.fetch_one(uuid)
        assert result[0] == uuid
        assert result[1] == "test.txt"
        assert result[2] == now
        assert result[3] == "Invoice"
        assert result[4] == "Permanent"
        assert result[5] == "Active"