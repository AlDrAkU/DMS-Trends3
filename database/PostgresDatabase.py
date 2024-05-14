import psycopg2
from .IDatabase import FileStorageRepository
from datetime import datetime
from typing import List

class PostgreSQLFileStorageRepository(FileStorageRepository):

    def insert(self,correlation_id: str, filepath: str, timestamp: datetime, doctype: str, temp_or_perm: str, status: str) -> None:
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
                host="localhost",
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
                        cursor.execute(update_query, (status, uuid))
            
            # Commit the transaction
            connection.commit()
            print("Status updated successfully!")
        except (Exception, psycopg2.Error) as error:
            print("Error while updating the status of the rows:", error)
