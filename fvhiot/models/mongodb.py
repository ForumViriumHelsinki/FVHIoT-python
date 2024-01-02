import datetime
from pydantic import field_validator, BaseModel, Extra


class Meta(BaseModel, extra=Extra.allow):
    """
    Check that device_id is present. All other metadata fields are optional.
    """

    device_id: str


class MongoDataline(BaseModel, extra=Extra.allow):
    """
    Check that data contains meta and a valid timezone aware datetime in time field
    """

    meta: Meta
    time: datetime.datetime

    @field_validator("time")
    @classmethod
    def time_must_be_aware(cls, v):
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("Datetime must be timezone aware, got naive datetime.")
        return v
