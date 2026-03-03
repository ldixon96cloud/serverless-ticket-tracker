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
        resp = table.get_item(Key={"ticketId": ticket_id})
    except ClientError as e:
        return err("Failed to fetch ticket", 500, {"code": e.response.get("Error", {}).get("Code")})

    item = resp.get("Item")
    if not item:
        return err("Ticket not found", 404)

    return ok(item, 200)
