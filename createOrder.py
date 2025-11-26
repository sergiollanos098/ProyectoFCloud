import json
import boto3  # type: ignore
import time
import uuid
from decimal import Decimal
from utils import build_response, to_plain

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('OrdersTable')
customers_table = dynamodb.Table('CustomersTable')

eventbridge = boto3.client('events')

ORDER_STAGES = [
    "received",
    "preparing",
    "packaging",
    "on_the_way",
    "completed",
]

def lambda_handler(event, context):
    body = json.loads(event["body"])

    tenantId = body["tenantId"]
    customerId = body["customerId"]

    # Validar si existe el cliente
    customer = customers_table.get_item(
        Key={"tenantId": tenantId, "customerId": customerId}
    )

    if "Item" not in customer:
        return build_response(400, {"error": "Customer does not exist"})

    orderId = "ORD-" + str(uuid.uuid4())[:8]

    # Convert total to Decimal for DynamoDB
    total_decimal = Decimal(str(body["total"]))
    now = int(time.time() * 1000)

    history_entry = {
        "stage": "received",
        "label": "Orden recibida",
        "timestamp": now
    }

    item = {
        "tenantId": tenantId,
        "orderId": orderId,
        "customerId": customerId,
        "items": body["items"],
        "total": total_decimal,
        "status": "received",
        "history": [history_entry],
        "addressId": body.get("addressId"),
        "createdAt": now
    }

    orders_table.put_item(Item=item)

    # Emitir evento order.created a EventBridge (optional future workflows)
    eventbridge.put_events(
        Entries=[
            {
                "Source": "order.service",
                "DetailType": "order.created",
                "Detail": json.dumps(to_plain(item))
            }
        ]
    )

    return build_response(200, {"message": "Order created", "order": item})
