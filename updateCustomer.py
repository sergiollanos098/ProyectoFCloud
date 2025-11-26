import json
import boto3
from utils import build_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CustomersTable')


def lambda_handler(event, context):
    customer_id = event["pathParameters"]["customerId"]
    body = json.loads(event["body"])
    tenant_id = body.get("tenantId", "kfc-peru")

    allowed_fields = {"firstName", "lastName", "phone", "email"}
    if not any(field in body for field in allowed_fields):
        return build_response(400, {"error": "No fields to update"})

    record = table.get_item(Key={"tenantId": tenant_id, "customerId": customer_id})
    if "Item" not in record:
        return build_response(404, {"error": "Customer not found"})

    item = record["Item"]

    for field in allowed_fields:
        if field in body:
            item[field] = body[field]

    # Maintain concatenated name field
    item["name"] = f"{item.get('firstName', '')} {item.get('lastName', '')}".strip()

    table.put_item(Item=item)

    return build_response(200, {"customer": item})

