import json
import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from common.response import ok, err
from common.validate import validate_enum, ALLOWED_STATUS, ALLOWED_PRIORITY, ALLOWED_CHANNEL

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def lambda_handler(event, context):
    ticket_id = (event.get("pathParameters") or {}).get("ticketId")
    if not ticket_id:
        return err("ticketId is required in path", 400)

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return err("Invalid JSON body", 400)

    status = body.get("status")
    priority = body.get("priority")
    channel = body.get("channel")
    title = body.get("title")
    description = body.get("description")

    if not any([status, priority, channel, title, description]):
        return err("No updatable fields provided", 400)

    if status is not None:
        v, msg = validate_enum(status, ALLOWED_STATUS, "status")
        if not v:
            return err(msg, 400)

    if priority is not None:
        v, msg = validate_enum(priority, ALLOWED_PRIORITY, "priority")
        if not v:
            return err(msg, 400)

    if channel is not None:
        v, msg = validate_enum(channel, ALLOWED_CHANNEL, "channel")
        if not v:
            return err(msg, 400)

    updates = []
    expr_vals = {}
    expr_names = {}

    def add_set(field, value):
        name_key = f"#{field}"
        val_key = f":{field}"
        expr_names[name_key] = field
        expr_vals[val_key] = value
        updates.append(f"{name_key} = {val_key}")

    if title is not None:
        add_set("title", title)
    if description is not None:
        add_set("description", description)
    if status is not None:
        add_set("status", status)
    if priority is not None:
        add_set("priority", priority)
    if channel is not None:
        add_set("channel", channel)

    add_set("updatedAt", _now_iso())

    update_expr = "SET " + ", ".join(updates)

    try:
        resp = table.update_item(
            Key={"ticketId": ticket_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_vals,
            ConditionExpression="attribute_exists(ticketId)",
            ReturnValues="ALL_NEW",
        )
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code == "ConditionalCheckFailedException":
            return err("Ticket not found", 404)
        return err("Failed to update ticket", 500, {"code": code})

    return ok(resp.get("Attributes", {}), 200)
