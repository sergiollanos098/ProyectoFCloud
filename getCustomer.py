import json
import boto3
from utils import build_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CustomersTable')

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    tenantId = params.get("tenantId", "kfc-peru")
    customerId = event["pathParameters"]["customerId"]

    response = table.get_item(
        Key={
            "tenantId": tenantId,
            "customerId": customerId
        }
    )

    if "Item" not in response:
        return build_response(404, {"error": "Customer not found"})

    return build_response(200, response["Item"])
