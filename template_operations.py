from flask import render_template
from jinja2 import Environment, FileSystemLoader
import json
import os

class TemplateOperations:
    def paycheckTemplate(self, fileName):    
        # Get the absolute path to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))

        # Define path to the JSON file
        json_file_path = os.path.join(project_dir, 'data', 'storage', 'temp', '2024-05-05', fileName)

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

    def invoiceTemplate(self,fileName):
        # Get the absolute path to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))

        # Define path to the JSON file
        json_file_path = os.path.join(project_dir, 'data', 'storage', 'temp', '2024-05-11', fileName)

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