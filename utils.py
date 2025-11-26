import json
from decimal import Decimal

DEFAULT_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*",
}


def to_plain(obj):
    """Recursively convert Decimals to floats for JSON serialization."""
    if isinstance(obj, list):
        return [to_plain(item) for item in obj]
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


def build_response(status_code, body):
    """Return a standard API Gateway response with CORS headers."""
    if not isinstance(body, (str, bytes)):
        body = json.dumps(to_plain(body))
    return {
        "statusCode": status_code,
        "headers": DEFAULT_HEADERS,
        "body": body,
    }

