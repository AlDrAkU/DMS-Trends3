import datetime
def build_response_message(correlation_id, status, message):
    response_message = {
        "correlation_id": correlation_id,
        "status": status,
        "timestamp": datetime.datetime.now().isoformat(),
        "message": message
    }
    return response_message