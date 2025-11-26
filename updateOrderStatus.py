import json
import time
import boto3
from utils import build_response, to_plain

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('OrdersTable')

ALLOWED_STATUSES = ["received", "preparing", "packaging", "on_the_way", "completed"]


def lambda_handler(event, context):
    order_id = event["pathParameters"]["orderId"]
    body = json.loads(event["body"])
    tenant_id = body.get("tenantId", "kfc-peru")
    new_status = body.get("status")
    operator = body.get("operator", "cook-ui")

    if new_status not in ALLOWED_STATUSES:
        return build_response(400, {"error": "Invalid status value"})

    timestamp = int(time.time() * 1000)
    history_entry = {
        "stage": new_status,
        "label": body.get("label") or status_to_label(new_status),
        "timestamp": timestamp,
        "operator": operator,
    }

    try:
        response = orders_table.update_item(
            Key={"tenantId": tenant_id, "orderId": order_id},
            ConditionExpression="attribute_exists(orderId)",
            UpdateExpression="SET #s = :status, history = list_append(if_not_exists(history, :empty), :entry)",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":status": new_status,
                ":entry": [history_entry],
                ":empty": [],
            },
            ReturnValues="ALL_NEW",
        )
    except orders_table.meta.client.exceptions.ConditionalCheckFailedException:
        return build_response(404, {"error": "Order not found"})

    updated = response.get("Attributes")
    if not updated:
        return build_response(404, {"error": "Order not found"})

    return build_response(200, {"order": to_plain(updated)})


def status_to_label(status):
    return {
        "received": "Orden recibida",
        "preparing": "En preparación",
        "packaging": "Empaquetando",
        "on_the_way": "En camino",
        "completed": "Completado",
    }.get(status, status)

