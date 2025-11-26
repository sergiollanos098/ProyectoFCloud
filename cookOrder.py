import json
import boto3
import time

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('OrdersTable')
events_table = dynamodb.Table('WorkflowEventsTable')
eventbridge = boto3.client('events')

def lambda_handler(event, context):
    detail = event["detail"]

    tenantId = detail["tenantId"]
    orderId = detail["orderId"]

    # Actualizar estado
    orders_table.update_item(
        Key={"tenantId": tenantId, "orderId": orderId},
        UpdateExpression="set #s = :status",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":status": "cooking"}
    )

    # Registrar evento en WorkflowEventsTable
    ts = int(time.time() * 1000)
    events_table.put_item(
        Item={
            "tenantId": tenantId,
            "orderId#timestamp": f"{orderId}#{ts}",
            "stage": "cooking",
            "startTime": ts,
            "operator": "cocinero-1"
        }
    )

    # Emitir evento a EventBridge
    eventbridge.put_events(
        Entries=[
            {
                "Source": "kitchen.service",
                "DetailType": "order.cooking.started",
                "Detail": json.dumps(detail)
            }
        ]
    )

    return {"statusCode": 200, "body": "Cooking started"}
