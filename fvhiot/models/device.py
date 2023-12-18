import datetime

from typing import Optional

from pydantic import BaseModel


class DeviceState(BaseModel):
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    last_seen_at: Optional[datetime.datetime] = None
    state: str = "Unknown"
    location: Optional[str] = None


class DeviceMetadata(BaseModel):
    device_type: str
    parser_module: str
    name: str
    pseudonym: Optional[str] = None
    description: str
    state: str
    device_in_redis: Optional[str] = None


class Device(BaseModel):
    device_id: str
    device_metadata: DeviceMetadata
    device_state: DeviceState


class PatchDeviceState(BaseModel):
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    last_seen_at: Optional[datetime.datetime]
    state: Optional[str]
    location: Optional[str]


class PatchDeviceMetadata(BaseModel):
    """
    Helper class for patching devices.
    """

    device_type: Optional[str]
    parser_module: Optional[str]
    name: Optional[str]
    pseudonym: Optional[str]
    description: Optional[str]
    state: Optional[str]
    device_in_redis: Optional[str]


class PatchDevice(BaseModel):
    """
    Helper class for patching devices.
    """

    device_id: str
    device_metadata: PatchDeviceMetadata
    device_state: PatchDeviceState


class StumpDevice(BaseModel):
    """
    Helper class for deleting many devices simultaneously. In such cases,
    we are only interested in device ids.
    """

    device_id: str
