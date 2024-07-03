from bson import Binary, ObjectId, json_util, Timestamp

def serialize_for_csv(data):
    if isinstance(data, Binary):
        return data.hex()  # Convert Binary to hex string
    elif isinstance(data, ObjectId):
        return str(data)  # Convert ObjectId to string
    elif isinstance(data, Timestamp):
        return str(data)  # Convert Timestamp to string
    elif isinstance(data, dict):
        return {k: serialize_for_csv(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_for_csv(item) for item in data]
    elif isinstance(data, bytes):
        return data.decode('utf-8', errors='replace')  # Convert bytes to string
    else:
        return data