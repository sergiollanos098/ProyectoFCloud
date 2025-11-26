import json
import boto3
from utils import build_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CustomersTable')

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        customer_id = body["customerId"]
        phone = body["phone"]

        # Buscar cliente
        response = table.get_item(
            Key={
                "tenantId": "kfc-peru",
                "customerId": customer_id
            }
        )

        if "Item" not in response:
            return build_response(404, {"error": "Customer not found"})

        customer = response["Item"]

        if customer["phone"] != phone:
            return build_response(401, {"error": "Invalid phone"})

        return build_response(200, {
            "message": "Login successful",
            "customer": customer
        })

    except Exception as e:
        return build_response(500, {"error": str(e)})
