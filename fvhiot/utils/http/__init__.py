def validate_data_from_request(data: dict) -> bool:
    """
    Check that all mandatory keys are in request data object

    :param data:
    :return:
    """
    # Check that mandatory keys are present in data
    for k in ["timestamp", "path", "url", "shceme", "request"]:
        if k not in data:
            return False
    # Check that mandatory keys are present data["request"]
    for k in ["method", "get", "post", "headers", "files", "body"]:
        if k not in data["request"]:
            return False
    return True
