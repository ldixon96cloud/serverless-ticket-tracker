import json
from typing import Any, Dict, Optional

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "GET,POST,PATCH,DELETE,OPTIONS",
}

def ok(body: Any, status_code: int = 200, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    h = dict(DEFAULT_HEADERS)
    if headers:
        h.update(headers)
    return {"statusCode": status_code, "headers": h, "body": json.dumps(body, default=str)}

def err(message: str, status_code: int = 400, details: Optional[Any] = None) -> Dict[str, Any]:
    payload = {"error": message}
    if details is not None:
        payload["details"] = details
    return ok(payload, status_code=status_code)
