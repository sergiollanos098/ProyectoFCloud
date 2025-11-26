import json
import boto3
import time
from utils import build_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CustomersTable')

def lambda_handler(event, context):
    body = json.loads(event["body"])

    first_name = body.get("firstName") or body.get("name", "").split(" ")[0]
    last_name = body.get("lastName") or " ".join(body.get("name", "").split(" ")[1:])

    full_name = f"{first_name or ''} {last_name or ''}".strip()

    item = {
        "tenantId": body["tenantId"],
        "customerId": body["customerId"],
        "firstName": (first_name or "").strip(),
        "lastName": (last_name or "").strip(),
        "name": full_name,
        "phone": body.get("phone", ""),
        "email": body.get("email", ""),
        "address": body.get("address", ""),
        "createdAt": int(time.time() * 1000)
    }

    table.put_item(Item=item)

    return build_response(200, {"message": "Customer created", "customer": item})
