import os
import boto3
from botocore.exceptions import ClientError

from common.response import ok, err

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    qs = event.get("queryStringParameters") or {}
    status_filter = qs.get("status")
    channel_filter = qs.get("channel")

    try:
        resp = table.scan()
    except ClientError as e:
        return err("Failed to list tickets", 500, {"code": e.response.get("Error", {}).get("Code")})

    items = resp.get("Items", [])

    if status_filter:
        items = [i for i in items if i.get("status") == status_filter]
    if channel_filter:
        items = [i for i in items if i.get("channel") == channel_filter]

    return ok({"count": len(items), "items": items}, 200)
