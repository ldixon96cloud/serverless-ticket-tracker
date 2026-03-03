import os
import boto3
from botocore.exceptions import ClientError

from common.response import ok, err

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    ticket_id = (event.get("pathParameters") or {}).get("ticketId")
    if not ticket_id:
        return err("ticketId is required in path", 400)

    try:
        table.delete_item(
            Key={"ticketId": ticket_id},
            ConditionExpression="attribute_exists(ticketId)"
        )
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code == "ConditionalCheckFailedException":
            return err("Ticket not found", 404)
        return err("Failed to delete ticket", 500, {"code": code})

    return ok({"deleted": True, "ticketId": ticket_id}, 200)
