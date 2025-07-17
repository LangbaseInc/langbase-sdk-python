AUTHORIZATION_HEADER = {
    "Authorization": "Bearer test-api-key",
}

JSON_CONTENT_TYPE_HEADER = {
    "Content-Type": "application/json",
}

AUTH_AND_JSON_CONTENT_HEADER = {
    **AUTHORIZATION_HEADER,
    **JSON_CONTENT_TYPE_HEADER,
}
