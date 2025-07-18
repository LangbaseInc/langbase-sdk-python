import types
from typing import Any, Dict, Literal, Type, Union, get_args, get_origin


def validate_response_headers(
    headers: Dict[str, Any], expected_headers: Dict[str, Any]
):
    """Validates that the response headers contain the expected headers."""
    for key, value in expected_headers.items():
        assert key in headers
        assert headers[key] == value


def validate_response_body(body: Dict[str, Any], response_type: Type):
    """Validates that the response body conforms to the given type."""
    if not hasattr(response_type, "__annotations__"):
        origin = get_origin(response_type)
        if origin:
            assert isinstance(body, origin)
        elif response_type is not Any:
            assert isinstance(body, response_type)
        return

    for key, value_type in response_type.__annotations__.items():
        if key in body and body[key] is not None:
            origin = get_origin(value_type)
            args = get_args(value_type)

            if origin is Literal:
                assert (
                    body[key] in args
                ), f"Field '{key}' has value '{body[key]}' which is not in Literal args {args}"
            elif origin is Union or origin is types.UnionType:
                # For now, we just pass on Union to avoid complexity.
                pass
            # Check if it's a TypedDict
            elif hasattr(value_type, "__annotations__"):
                validate_response_body(body[key], value_type)
            elif origin:  # This handles list, dict, etc.
                assert isinstance(
                    body[key], origin
                ), f"Field '{key}' has wrong type. Expected {origin}, got {type(body[key])}"
            elif value_type is not Any:
                assert isinstance(
                    body[key], value_type
                ), f"Field '{key}' has wrong type. Expected {value_type}, got {type(body[key])}"
