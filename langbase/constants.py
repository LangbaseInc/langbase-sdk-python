"""Constants used in the Langbase SDK."""

from typing import Dict

STATUS_CODE_TO_MESSAGE: Dict[int, str] = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    409: "Conflict",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}

ERROR_MAP: Dict[int, str] = {
    400: "BadRequestError",
    401: "AuthenticationError",
    403: "PermissionDeniedError",
    404: "NotFoundError",
    409: "ConflictError",
    422: "UnprocessableEntityError",
    429: "RateLimitError",
}

BASE_URL = "https://api.langbase.com"
# API Endpoints
PIPES_ENDPOINT = "/v1/pipes"
PIPE_DETAIL_ENDPOINT = "/v1/pipes/{name}"
PIPE_RUN_ENDPOINT = "/v1/pipes/run"

MEMORY_ENDPOINT = "/v1/memory"
MEMORY_DETAIL_ENDPOINT = "/v1/memory/{name}"
MEMORY_RETRIEVE_ENDPOINT = "/v1/memory/retrieve"
MEMORY_DOCUMENTS_ENDPOINT = "/v1/memory/{memory_name}/documents"
MEMORY_DOCUMENT_DETAIL_ENDPOINT = "/v1/memory/{memory_name}/documents/{document_name}"
MEMORY_DOCUMENTS_UPLOAD_ENDPOINT = "/v1/memory/documents"
MEMORY_DOCUMENT_EMBEDDINGS_RETRY_ENDPOINT = (
    "/v1/memory/{memory_name}/documents/{document_name}/embeddings/retry"
)

TOOLS_CRAWL_ENDPOINT = "/v1/tools/crawl"
TOOLS_WEB_SEARCH_ENDPOINT = "/v1/tools/web-search"

THREADS_ENDPOINT = "/v1/threads"
THREAD_DETAIL_ENDPOINT = "/v1/threads/{thread_id}"
THREAD_MESSAGES_ENDPOINT = "/v1/threads/{thread_id}/messages"

EMBED_ENDPOINT = "/v1/embed"
CHUNKER_ENDPOINT = "/v1/chunker"
PARSER_ENDPOINT = "/v1/parser"
AGENT_RUN_ENDPOINT = "/v1/agent/run"
