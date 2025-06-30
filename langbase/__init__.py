"""
Langbase Python SDK.

This package provides a Python interface to the Langbase API, allowing you to
build and deploy AI-powered applications using Langbase's infrastructure.

Basic usage:

```python
from langbase import Langbase

# Initialize the client
lb = Langbase(api_key="your-api-key")

# Run a pipe
response = lb.pipes.run(
    name="your-pipe-name",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about AI."}
    ]
)

print(response["completion"])
```
"""

from .client import Langbase
from .errors import (
    APIError, APIConnectionError, APIConnectionTimeoutError,
    BadRequestError, AuthenticationError, PermissionDeniedError,
    NotFoundError, ConflictError, UnprocessableEntityError,
    RateLimitError, InternalServerError
)

__version__ = "0.1.0"
__all__ = [
    'Langbase',
    'APIError',
    'APIConnectionError',
    'APIConnectionTimeoutError',
    'BadRequestError',
    'AuthenticationError',
    'PermissionDeniedError',
    'NotFoundError',
    'ConflictError',
    'UnprocessableEntityError',
    'RateLimitError',
    'InternalServerError',
]
