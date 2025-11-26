import json
import boto3
from boto3.dynamodb.conditions import Key
from utils import build_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AddressesTable')


def lambda_handler(event, context):
    customer_id = event["pathParameters"]["customerId"]
    address_id = event["pathParameters"]["addressId"]
    body = json.loads(event["body"])
    tenant_id = body.get("tenantId", "kfc-peru")

    key = {"tenantId": tenant_id, "customerKey": f"{customer_id}#{address_id}"}
    record = table.get_item(Key=key)
    if "Item" not in record:
        return build_response(404, {"error": "Address not found"})

    item = record["Item"]

    for field in ["label", "line1", "reference", "city"]:
        if field in body:
            item[field] = body[field]

    if "isDefault" in body:
        item["isDefault"] = bool(body["isDefault"])

    table.put_item(Item=item)

    if item.get("isDefault"):
        _clear_other_defaults(tenant_id, customer_id, address_id)

    return build_response(200, {"address": item})


def _clear_other_defaults(tenant_id, customer_id, current_address_id):
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

