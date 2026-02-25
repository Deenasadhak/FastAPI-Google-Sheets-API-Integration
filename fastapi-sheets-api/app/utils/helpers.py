# File: app/utils/helpers.py
from typing import Any, Dict, Optional

def format_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """
    Format a consistent success JSON response.
    """
    return {
        "status": "success",
        "message": message,
        "data": data
    }


def format_error_response(message: str, details: Optional[Any] = None) -> Dict[str, Any]:
    """
    Format a consistent error JSON response.
    """
    response = {
        "status": "error",
        "message": message
    }
    if details:
        response["details"] = details
    return response

