#Tests for the Postgres database
import sys
import os
module_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(module_dir)
sys.path.append(parent_dir)

import secrets
import unittest
from database.PostgresDatabase import PostgreSQLFileStorageRepository
from database.IDatabase import FileStorageRepository

class TestPostgresDatabase(unittest.TestCase):
    def setUp(self):
        self.postgres = PostgreSQLFileStorageRepository()
        self.connection = self.postgres.connect()
        self.cursor = self.connection.cursor()

    def test_insert(self):
        # Test the insert method
        uuid = secrets.token_hex(4)
        self.postgres.insert(uuid, "test.txt", "Permanent", "Active")
        # self.cursor.execute("SELECT * FROM FileStorage WHERE UUIDColumn = '12345'")
        # result = self.cursor.fetchone()
        result = self.postgres.fetch_one(uuid)
        assert result[0] == uuid
        assert result[1] == "test.txt"
        assert result[2] == "Permanent"
        assert result[3] == "Active"