import datetime
import xml.etree.ElementTree as ET
def build_response_message(correlation_id, status, message):
    response_message = {
        "correlation_id": correlation_id,
        "status": status,
        "timestamp": datetime.datetime.now().isoformat(),
        "message": message
    }
    return response_message

def map_to_json(body):
    # Parse the XML body into DocTypeModel
    xml_data = body.decode()  # Assuming body contains XML as string
    xml_data = xml_data.replace("{", "").replace("}", "")
    root = ET.fromstring(xml_data)
    # Convert the ElementTree into a dictionary
    # Initialize an empty dictionary to hold the parsed data
    data = {}
    # Iterate through each child element of the root
    for child in root:
        # Check if the child element has sub-elements
        if len(child) > 0:
            # If yes, initialize a sub-dictionary to hold its sub-elements
            sub_data = {}
            # Iterate through each sub-element
            for sub_child in child:
                # Check if the sub-element has sub-elements
                if len(sub_child) > 0:
                    # If yes, initialize a sub-sub-dictionary to hold its sub-elements
                    sub_sub_data = {}
                    # Iterate through each sub-sub-element
                    for sub_sub_child in sub_child:
                        # Add the sub-sub-element's tag and text to the sub-sub-dictionary
                        sub_sub_data[sub_sub_child.tag] = sub_sub_child.text.strip() if sub_sub_child.text else None
                    # Add the sub-sub-dictionary to the sub-dictionary under the tag of the sub-element
                    sub_data[sub_child.tag] = sub_sub_data
                else:
                    # If the sub-element has no sub-elements, directly add its tag and text to the sub-dictionary
                    sub_data[sub_child.tag] = sub_child.text.strip() if sub_child.text else None
            # Add the sub-dictionary to the main data dictionary under the tag of the child element
            data[child.tag] = sub_data
        else:
            # If the child element has no sub-elements, directly add its tag and text to the main data dictionary
            data[child.tag] = child.text.strip() if child.text else None
    return data