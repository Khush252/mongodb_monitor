from bson import Binary, ObjectId, Timestamp, json_util

# Serialization because csv supports only particular data types
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
    else:
        return data
