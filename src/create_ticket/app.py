import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from common.response import ok, err
from common.validate import require_fields, validate_enum, ALLOWED_PRIORITY, ALLOWED_CHANNEL

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return err("Invalid JSON body", 400)

    valid, missing = require_fields(body, ["title", "description"])
    if not valid:
        return err("Missing required fields", 400, {"missing": missing})

    priority = body.get("priority", "MEDIUM")
    channel = body.get("channel", "POS")

    v, msg = validate_enum(priority, ALLOWED_PRIORITY, "priority")
    if not v:
        return err(msg, 400)
    v, msg = validate_enum(channel, ALLOWED_CHANNEL, "channel")
    if not v:
        return err(msg, 400)

    ticket_id = str(uuid.uuid4())
    now = _now_iso()

    item = {
        "ticketId": ticket_id,
        "title": body["title"],
        "description": body["description"],
        "status": "OPEN",
        "priority": priority,
        "channel": channel,
        "createdAt": now,
        "updatedAt": now,
    }

    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(ticketId)"
        )
    except ClientError as e:
        return err("Failed to create ticket", 500, {"code": e.response.get("Error", {}).get("Code")})

    return ok(item, 201)
