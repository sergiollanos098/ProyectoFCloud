import json
import time
import uuid
import boto3
from boto3.dynamodb.conditions import Key
from utils import build_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AddressesTable')


def lambda_handler(event, context):
    customer_id = event["pathParameters"]["customerId"]
    body = json.loads(event["body"])
    tenant_id = body.get("tenantId", "kfc-peru")

    address_id = "ADDR-" + uuid.uuid4().hex[:8]
    now = int(time.time() * 1000)

    item = {
        "tenantId": tenant_id,
        "customerKey": f"{customer_id}#{address_id}",
        "customerId": customer_id,
        "addressId": address_id,
        "label": body.get("label", "Dirección"),
        "line1": body.get("line1", ""),
        "reference": body.get("reference", ""),
        "city": body.get("city", ""),
        "isDefault": body.get("isDefault", False),
        "createdAt": now,
    }

    table.put_item(Item=item)

    if item["isDefault"]:
        _clear_other_defaults(tenant_id, customer_id, address_id)

    return build_response(200, {"address": item})


def _clear_other_defaults(tenant_id, customer_id, current_address_id):
    """Ensure only one default address per customer."""
    response = table.query(
        KeyConditionExpression=Key("tenantId").eq(tenant_id) & Key("customerKey").begins_with(f"{customer_id}#")
    )
    for addr in response.get("Items", []):
        if addr["addressId"] == current_address_id:
            continue
        if addr.get("isDefault"):
            table.update_item(
                Key={"tenantId": tenant_id, "customerKey": f"{customer_id}#{addr['addressId']}"},
                UpdateExpression="SET isDefault = :false",
                ExpressionAttributeValues={":false": False},
            )

