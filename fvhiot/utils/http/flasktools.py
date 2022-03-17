import datetime
import flask


def extract_data_from_flask_request(request: flask.request) -> dict:
    """
    Extract all available data from `flask.request` and put it into a dict.
    NOTE: all other extractors (e.g. Django) should follow this structure.

    :param request: flask.request
    :return: dict containing request data
    """
    data = {
        "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        "path": request.path,
        "url": request.url,
        "scheme": request.scheme,
        "remote_addr": request.remote_addr,
        "request": {
            "method": request.method,
            "get": dict(request.args),
            "post": dict(request.form),
            "headers": dict(request.headers),
            "files": {},
            "body": b"",
        },
    }
    # Check for form files
    if request.method == "POST":
        for fn in request.files.keys():
            data["request"]["files"]["fn"] = request.files[fn].read()
    # If there were no files, put request body to the data as is
    if data["request"]["files"] == {}:
        data["request"]["body"] = request.data
    return data
