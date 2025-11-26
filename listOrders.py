import boto3
from boto3.dynamodb.conditions import Key
from utils import build_response, to_plain

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('OrdersTable')


def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    tenant_id = params.get("tenantId", "kfc-peru")
    customer_id = params.get("customerId")
    status_filter = params.get("status")

    orders = []
    last_key = None

    while True:
        query_kwargs = {
            "KeyConditionExpression": Key("tenantId").eq(tenant_id)
        }
        if last_key:
            query_kwargs["ExclusiveStartKey"] = last_key

        response = orders_table.query(**query_kwargs)
        items = response.get("Items", [])

        for item in items:
            if customer_id and item.get("customerId") != customer_id:
                continue
            if status_filter and item.get("status") != status_filter:
                continue
            orders.append(item)

        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break

    # Sort newest first
    orders.sort(key=lambda x: x.get("createdAt", 0), reverse=True)

    return build_response(200, {"orders": to_plain(orders)})

