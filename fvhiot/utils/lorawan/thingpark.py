from ...models.thingpark import DevEuiUplink
import json


def get_uplink_obj(data: dict) -> DevEuiUplink:
    """
    Return DevEuiUplink object from data
    data contains request body in binary format
    """
    request_body_binary = data["request"]["body"]
    body_data = json.loads(request_body_binary.decode())
    uplink_obj = DevEuiUplink(**body_data["DevEUI_uplink"])
    return uplink_obj
