"""
Pydantic schemas to enforce data types.

See: https://stackoverflow.com/questions/69617489/can-i-get-incoming-extra-fields-from-pydantic
for one way of handling extra fields. Here they are simply added as an extra dict to the schema.


We could do also this:

class RequestModel(BaseModel):
    method: str
    get: dict
    url: str
    post: dict
    headers: dict
    files: dict
    body: bytes

    class Config:
        extra = "allow"
"""


from pydantic import BaseModel, StrictStr, StrictBytes


class RequestData(BaseModel):
    method: StrictStr
    get: dict
    post: dict
    headers: dict
    files: dict
    body: StrictBytes
    # extra: Dict[str, Any]
    #
    # @model_validator(mode="before")
    # @classmethod
    # def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
    #     all_required_field_names = {field.alias for field in cls.model_fields.values() if field.alias != "extra"}
    #     extra: Dict[str, Any] = {}
    #     for field_name in list(values):
    #         if field_name not in all_required_field_names:
    #             extra[field_name] = values.pop(field_name)
    #     values["extra"] = extra
    #     return values


class RequestModel(BaseModel):
    timestamp: StrictStr
    path: StrictStr
    url: StrictStr
    scheme: StrictStr
    remote_addr: StrictStr
    request: RequestData
    # extra: Dict[str, Any]
    #
    # @model_validator(mode="before")
    # @classmethod
    # def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
    #     all_required_field_names = {field.alias for field in cls.model_fields.values() if field.alias != "extra"}
    #     extra: Dict[str, Any] = {}
    #     for field_name in list(values):
    #         if field_name not in all_required_field_names:
    #             extra[field_name] = values.pop(field_name)
    #     values["extra"] = extra
    #     print("MOIOIIII", values)
    #     return values
