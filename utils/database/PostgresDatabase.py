import os
from datetime import datetime
from typing import List

import psycopg2

from .IDatabase import FileStorageRepository


class PostgreSQLFileStorageRepository(FileStorageRepository):
    def __init__(self, postgres_user: str = "postgres", postgres_password: str = "postgres",
                 postgres_host: str = "postgres",
                 # if you are using docker-compose, use the service name else use localhost
                 postgres_port: str = "5432", postgres_database: str = "DMS"):
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password
        self.postgres_host = postgres_host
        self.postgres_port = postgres_port
        self.postgres_database = postgres_database

    def insert(self, correlation_id: str, filepath: str, timestamp: datetime, doctype: str, temp_or_perm: str,
               status: str) -> None:
        """
        Insert a new row into the FileStorage table in PostgreSQL.

        :param filepath: File path
        :param TimeStamp: TimeStamp
        :param DocType: Invoice, Paycheck or Other
        :param temp_or_perm: Temporary or Permanent status
        :param status: Status (Active or Deleted)
        :return: None
        """
        try:
            # SQL statement for insertion
            insert_query = """
            INSERT INTO FileStorage (UUIDColumn, FilePath, TimeStamp, DocType, TempOrPerm, Status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            # Execute the SQL statement
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(insert_query, (correlation_id, filepath, timestamp, doctype, temp_or_perm, status))

            # Commit the transaction
            connection.commit()
            print("Row inserted successfully!")
        except (Exception, psycopg2.Error) as error:
            print("Error while inserting into the table:", error)

    def fetch_one(self, uuid: str):
        """
        Fetch one row from the FileStorage table by UUID.

        :param uuid: UUID
        :return: None
        """
        try:
            # SQL statement for fetching one row by UUID
            select_query = """
            SELECT * FROM FileStorage WHERE UUIDColumn = %s
            """

            # Execute the SQL statement
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(select_query, (uuid,))
                    row = cursor.fetchone()
                    print(row)
                    return row
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching from the table:", error)

    def fetch_all(self):
        """
        Fetch all rows from the FileStorage table.

        :return: None
        """
        try:
            # SQL statement for fetching all rows
            select_query = """
            SELECT * FROM FileStorage
            """

            # Execute the SQL statement
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(select_query)
                    rows = cursor.fetchall()
                    return rows
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching from the table:", error)

    # Function that establishes a connection to the PostgreSQL database
    def connect(self):
        try:
            # Connect to the PostgreSQL database
            connection = psycopg2.connect(
                user="postgres",
                password="postgres", #TODO secrets.PASSWORD,
                host=self.postgres_host,
                port="5432",
                database="DMS",
            )
            return connection
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def update_status_of_list(self, uuids: List[str], status: str):
        """
        Update the status of all rows in the FileStorage table with UUIDs in the given list.

        :param uuids: List of UUIDs
        :param status: Status (Active or Deleted)
        :return: None
        """
        try:
            # SQL statement for updating the status of selected rows
            update_query = """
            UPDATE FileStorage SET Status = %s WHERE UUIDColumn = %s
            """

            # Execute the SQL statement
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    for uuid in uuids:

                        cursor.execute(update_query, (status, uuid.split(".")[0]))
            
            # Commit the transaction
            connection.commit()
            print("Status updated successfully!")
        except (Exception, psycopg2.Error) as error:
            print("Error while updating the status of the rows:", error)
            
    def insert_gdpr(self, original_name: str, uuid: str) -> None:
        """
        Insert a new row into the Gdpr table in PostgreSQL.

        :param original_name: Original name in the file
        :param uuid: UUID
        :return: None
        """
        try:
            # SQL statement for insertion
            insert_query = """
            INSERT INTO Gdpr (original_name, anonymized_id)
            VALUES (%s, %s)
            """

            # Execute the SQL statement
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(insert_query, (original_name, uuid))

            # Commit the transaction
            connection.commit()
            print("Row inserted successfully!")
        except (Exception, psycopg2.Error) as error:
            print("Error while inserting into the table:", error)

    def fetch_one_gdpr(self, uuid: str):
        """
        Fetch one row from the Gdpr table by UUID.

        :param uuid: UUID
        :return: None
        """
        try:
            # SQL statement for fetching one row by anonymized_id
            select_query = """
            SELECT * FROM Gdpr WHERE anonymized_id = %s
            """

            # Execute the SQL statement
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(select_query, (uuid,))
                    row = cursor.fetchone()
                    print(row)
                    return row
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching from the table:", error)