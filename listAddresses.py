import boto3
from boto3.dynamodb.conditions import Key
from utils import build_response, to_plain

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AddressesTable')


def lambda_handler(event, context):
    customer_id = event["pathParameters"]["customerId"]
    params = event.get("queryStringParameters") or {}
    tenant_id = params.get("tenantId", "kfc-peru")

    response = table.query(
        KeyConditionExpression=Key("tenantId").eq(tenant_id) & Key("customerKey").begins_with(f"{customer_id}#")
    )

    addresses = response.get("Items", [])
    addresses.sort(key=lambda x: x.get("createdAt", 0), reverse=True)

    return build_response(200, {"addresses": to_plain(addresses)})

