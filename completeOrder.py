import json
import boto3
import time

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('OrdersTable')
events_table = dynamodb.Table('WorkflowEventsTable')

def lambda_handler(event, context):
    detail = event["detail"]

    tenantId = detail["tenantId"]
    orderId = detail["orderId"]

    # Cambiar estado a completado
    orders_table.update_item(
        Key={"tenantId": tenantId, "orderId": orderId},
        UpdateExpression="set #s = :status",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":status": "completed"}
    )

    ts = int(time.time() * 1000)
    events_table.put_item(
        Item={
            "tenantId": tenantId,
            "orderId#timestamp": f"{orderId}#{ts}",
            "stage": "completed",
            "endTime": ts,
            "operator": "sistema"
        }
    )

    return {"statusCode": 200, "body": "Order completed"}
