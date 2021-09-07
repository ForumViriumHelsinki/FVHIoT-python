import datetime
import flask
from starlette.datastructures import UploadFile
from starlette.requests import Request


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
        "request": {
            "method": request.method,
            "get": dict(request.args),
            "post": dict(request.form),
            "headers": dict(request.headers),
            "files": {},
            "body": b"",
        },
        "remote_addr": request.remote_addr,
    }
    if request.method == "POST":
        for fn in request.files.keys():
            data["request"]["files"]["fn"] = request.files[fn].read()
    if data["request"]["files"] == {}:
        data["request"]["body"] = request.data
    return data


async def extract_data_from_starlette_request(request: Request) -> dict:
    """
    Extract all available data from `starlette.requests.Request` and put it into a dict.
    NOTE: all other extractors (e.g. Django) should follow this structure.

    :param request: starlette.requests.Request
    :return: dict containing request data
    """
    data = {
        "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        "path": request.url.path,
        "url": str(request.url),
        "scheme": request.url.scheme,
        "request": {
            "method": request.method,
            "get": dict(request.query_params),
            "post": {},
            "headers": dict(request.headers),
            "files": {},
            "body": b"",
        },
    }
    # Form text and file fields are available after .form() call
    # https://www.starlette.io/requests/#request-files
    formdata = await request.form()
    for k in formdata.keys():
        if isinstance(formdata[k], str):
            data["request"]["post"][k] = formdata[k]
        elif isinstance(formdata[k], UploadFile):
            f: UploadFile = formdata[k]
            data["request"]["files"][k] = await f.read()
    # If form was not detected, read request.body() (even if it is empty)
    if data["request"]["files"] == {}:
        data["request"]["body"] = await request.body()
    return data
