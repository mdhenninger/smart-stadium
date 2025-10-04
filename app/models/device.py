"""Pydantic models and domain objects for device management."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    WIZ = "wiz"


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class DeviceInfo(BaseModel):
    device_id: str = Field(..., description="Unique identifier for the device")
    ip_address: str = Field(..., description="IP address of the smart device")
    name: str = Field(..., description="Friendly display name")
    location: str | None = Field(None, description="Physical location description")
    enabled: bool = Field(True, description="Whether device should actively participate")
    device_type: DeviceType = Field(DeviceType.WIZ, description="Type of smart device")
    last_seen: Optional[datetime] = Field(None, description="Last successful communication time")
    response_time_ms: Optional[float] = Field(None, description="Last known response latency in milliseconds")
    status: DeviceStatus = Field(DeviceStatus.UNKNOWN, description="Current status of the device")


class DeviceSummary(BaseModel):
    total_devices: int
    enabled_devices: int
    online_devices: int
    offline_devices: int
