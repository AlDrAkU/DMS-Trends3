import datetime
import os
import xml.etree.ElementTree as ET

from utils.database.PostgresDatabase import PostgreSQLFileStorageRepository


def build_response_message(correlation_id, status, message):
    response_message = {
        "correlation_id": correlation_id,
        "status": status,
        "timestamp": datetime.datetime.now().isoformat(),
        "message": message
    }
    return response_message

def map_to_json(body):
    xml_data = body.decode()  # Assuming body contains XML as string
    xml_data = xml_data.replace("{", "").replace("}", "")
    root = ET.fromstring(xml_data)

    def parse_element(element):
        if len(element) > 0:
            if len(set(child.tag for child in element)) == len(element):  # All tags are unique
                return {child.tag: parse_element(child) for child in element}
            else:  # There are duplicate tags, return a list of dictionaries
                return [parse_element(child) for child in element]
        else:
            return element.text.strip() if element.text else None

    data = parse_element(root)
    return data


def delete_temporary_files():
    # Delete temporary files
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Define path to the JSON file
    temp_files = os.path.join(project_dir, 'data', 'storage', 'temp')
    files_deleted = []
    for root, dirs, files in os.walk(temp_files):
        for file in files:
            if file != 'invoice.json' and file != 'paycheck.json':
                os.remove(os.path.join(root, file))
                files_deleted.append(file)
        if not os.listdir(root):
            os.rmdir(root)

    PostgreSQLFileStorageRepository().update_status_of_list(files_deleted, "Deleted")
    
    return build_response_message((" ").join(files_deleted), "Temporary files deleted successfully", "Temporary files deleted successfully")

def get_config_directory():
    # Get the directory of the utils
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Get the direcctory of the repository_service
    script_dir = os.path.dirname(script_dir)

    # Construct the path to the config.json file
    config_path = os.path.join(script_dir, 'config.json')

    return config_path