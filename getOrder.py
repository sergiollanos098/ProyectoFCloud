import json
import boto3
from utils import build_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('OrdersTable')

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    tenantId = params.get("tenantId", "kfc-peru")
    orderId = event["pathParameters"]["orderId"]

    response = table.get_item(
        Key={
            "tenantId": tenantId,
            "orderId": orderId
        }
    )

    if "Item" not in response:
        return build_response(404, {"error": "Order not found"})

    return build_response(200, response["Item"])
