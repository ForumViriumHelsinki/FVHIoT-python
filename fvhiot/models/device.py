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
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    last_seen_at: Optional[datetime.datetime] = None
    state: Optional[str] = None
    location: Optional[str] = None


class PatchDeviceMetadata(BaseModel):
    """
    Helper class for patching devices.
    """

    device_type: Optional[str] = None
    parser_module: Optional[str] = None
    name: Optional[str] = None
    pseudonym: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    device_in_redis: Optional[str] = None


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
