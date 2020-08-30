import datetime
import flask


def extract_data_from_flask_request(request: flask.request):
    """
    Extract all available data from `flask.request` and put it into a dict.
    NOTE: all other extractors (e.g. Django) should follow this structure.

    :param request: flask.request
    :return: dict containing request data
    """
    data = {
        'timestamp': datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        'request': {
            'method': request.method,
            'get': dict(request.args),
            'post': dict(request.form),
            'headers': dict(request.headers),
        }
    }
    data['request']['body'] = request.data if isinstance(request.data, bytes) else dict(request.data)
    for attr in ['remote_addr', 'scheme']:
        data['request'][attr] = getattr(request, attr)
    return data
