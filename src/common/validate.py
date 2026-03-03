from typing import Any, Dict, List, Tuple

ALLOWED_STATUS = {"OPEN", "IN_PROGRESS", "RESOLVED"}
ALLOWED_PRIORITY = {"LOW", "MEDIUM", "HIGH"}
ALLOWED_CHANNEL = {"KIOSK", "POS", "DMB", "DELIVERY"}

def require_fields(payload: Dict[str, Any], fields: List[str]) -> Tuple[bool, List[str]]:
    missing = [f for f in fields if f not in payload or payload[f] in (None, "")]
    return (len(missing) == 0, missing)

def validate_enum(value: Any, allowed: set, field: str) -> Tuple[bool, str]:
    if value is None:
        return True, ""
    if value not in allowed:
        return False, f"{field} must be one of {sorted(list(allowed))}"
    return True, ""
