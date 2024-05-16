import json
import os

from flask import render_template
from jinja2 import Environment, FileSystemLoader

from utils.database.PostgresDatabase import PostgreSQLFileStorageRepository


class TemplateOperations:
    def paycheckTemplate(self, fileName,uuid:str = None):
        # Get the absolute path to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        if uuid:
            # Fetch the data from the database
            record = PostgreSQLFileStorageRepository().fetch_one(uuid)
            mapped_record = {
                "UUIDColumn": record[0],
                "FilePath": record[1],
                "TimeStamp": record[2],
                "DocType": record[3],
                "TempOrPerm": record[4],
                "Status": record[5]
            }
            json_file_path = os.path.join(project_dir, 'data', 'storage', 'temp', mapped_record.get("FilePath").split("/")[-1],mapped_record.get("UUIDColumn")+".json")
            print('used uuid:',json_file_path)
        # Define path to the JSON file
        else:
            json_file_path = os.path.join(project_dir, 'data', 'storage', 'temp', fileName)

        # Load JSON data from file
        with open(json_file_path) as json_file:
            user_data = json.load(json_file)

        # Construct the absolute path to the templates directory
        templates_dir = os.path.join(project_dir, 'templates')

        env = Environment(loader=FileSystemLoader(templates_dir))
        try:
            template = env.get_template('paycheck_template.html')
        except:
            return "Template not found"
        # Render template with JSON data
        return render_template(template, **user_data)

    def invoiceTemplate(self,fileName,uuid: str = None):
        # Get the absolute path to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        if uuid:
            # Fetch the data from the database
            record = PostgreSQLFileStorageRepository().fetch_one(uuid)
            mapped_record = {
                "UUIDColumn": record[0],
                "FilePath": record[1],
                "TimeStamp": record[2],
                "DocType": record[3],
                "TempOrPerm": record[4],
                "Status": record[5]
            }
            json_file_path = os.path.join(project_dir, 'data', 'storage', 'temp', mapped_record.get("FilePath").split("/")[-1],mapped_record.get("UUIDColumn")+".json")
            print('used uuid:',json_file_path)
        # Define path to the JSON file
        else:
            json_file_path = os.path.join(project_dir, 'data', 'storage', 'temp', fileName)

        # Load JSON data from file
        with open(json_file_path) as json_file:
            user_data = json.load(json_file)

        # Construct the absolute path to the templates directory
        templates_dir = os.path.join(project_dir, 'templates')

        env = Environment(loader=FileSystemLoader(templates_dir))
        try:
            template = env.get_template('invoice_template.html')
        except:
            return "Template not found"

        # Render template with JSON data
        return render_template(template, **user_data)
    
    def viewFilesTemplate_All(self):
        # Get template
        template = self.getTemplate('view_files_template.html')

        # Fetch the data from the database
        records = PostgreSQLFileStorageRepository().fetch_all()
        mapped_records = self.map_records(records)
        print(records)

        # Render template
        return render_template(template, records=mapped_records)
    
    def viewFilesTemplate_Single(self, uuid: str):
        # Get template
        template = self.getTemplate('view_files_template.html')

        # Fetch the data from the database
        record = PostgreSQLFileStorageRepository().fetch_one(uuid)
        mapped_record = [{
                "UUIDColumn": record[0],
                "FilePath": record[1],
                "TimeStamp": record[2],
                "DocType": record[3],
                "TempOrPerm": record[4],
                "Status": record[5]
            }]
        print(record)

        # Render template
        return render_template(template, records=mapped_record)
    
    def getTemplate(self, templateName: str):
        # Get the absolute path to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))

        # Define path to the templates directory
        templates_dir = os.path.join(project_dir, 'templates')

        env = Environment(loader=FileSystemLoader(templates_dir))
        try:
            return env.get_template(templateName)
        except:
            return "Template not found"
    
    def map_records(self, records):
        # Define a list to store mapped records
        mapped_records = []

        # Iterate over each record
        for record in records:
            # Map the fields to a dictionary
            mapped_record = {
                "UUIDColumn": record[0],
                "FilePath": record[1],
                "TimeStamp": record[2],
                "DocType": record[3],
                "TempOrPerm": record[4],
                "Status": record[5]
            }
            # Append the mapped record to the list
            mapped_records.append(mapped_record)

        return mapped_records
        