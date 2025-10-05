"""Device management service for Smart Stadium."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Dict, Iterable

from app.core.config_manager import AppConfig
from app.models.device import DeviceInfo, DeviceStatus, DeviceSummary, DeviceType, LightType
from app.services.history_store import HistoryStore
from app.services.lights_service import LightsService
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DeviceManager:
    """Tracks configured devices and provides control hooks."""

    def __init__(self, config: AppConfig, lights_service: LightsService, history_store: HistoryStore):
        self._config = config
        self._lights = lights_service
        self._history = history_store
        self._devices: Dict[str, DeviceInfo] = {}
        self._load_from_config()

    def _load_from_config(self) -> None:
        # Load WiZ devices
        wiz_devices = self._config.wiz_config.get("devices", [])
        for entry in wiz_devices:
            ip = entry.get("ip")
            if not ip:
                continue
            device_id = f"wiz_{ip.replace('.', '_')}"
            
            # Parse light_type from config
            light_type_str = entry.get("light_type")
            light_type = None
            if light_type_str:
                try:
                    light_type = LightType(light_type_str)
                except ValueError:
                    light_type = LightType.LAMP  # Default fallback
            
            device = DeviceInfo(
                device_id=device_id,
                ip_address=ip,
                name=entry.get("name", device_id),
                location=entry.get("location"),
                enabled=bool(entry.get("enabled", True)),
                device_type=DeviceType.WIZ,
                light_type=light_type,
            )
            self._devices[device_id] = device
        
        # Load Govee devices
        govee_devices = self._config.govee_config.get("devices", [])
        for entry in govee_devices:
            device_id_mac = entry.get("device_id")
            if not device_id_mac:
                continue
            # Use last 8 chars of MAC for shorter device_id
            device_id = f"govee_{device_id_mac[-8:].replace(':', '_')}"
            device = DeviceInfo(
                device_id=device_id,
                ip_address="cloud",  # Govee uses cloud API, not direct IP
                name=entry.get("name", device_id),
                location=entry.get("location"),
                enabled=bool(entry.get("enabled", True)),
                device_type=DeviceType.GOVEE,
            )
            self._devices[device_id] = device

    def list_devices(self) -> Iterable[DeviceInfo]:
        return self._devices.values()

    def get_device(self, device_id: str) -> DeviceInfo | None:
        return self._devices.get(device_id)

    def summary(self) -> DeviceSummary:
        total = len(self._devices)
        enabled_devices = sum(1 for d in self._devices.values() if d.enabled)
        online_devices = sum(1 for d in self._devices.values() if d.status == DeviceStatus.ONLINE)
        offline_devices = sum(1 for d in self._devices.values() if d.status == DeviceStatus.OFFLINE)
        return DeviceSummary(
            total_devices=total,
            enabled_devices=enabled_devices,
            online_devices=online_devices,
            offline_devices=offline_devices,
        )

    async def refresh_status(self) -> None:
        """Ping lights and update cached metadata for each device individually."""

        logger.debug("Refreshing device status for %s devices", len(self._devices))
        start = datetime.now(timezone.utc)
        
        # Get list of enabled WiZ device IPs to check
        enabled_wiz_ips = [
            device.ip_address 
            for device in self._devices.values() 
            if device.device_type == DeviceType.WIZ and device.enabled
        ]
        
        # Get per-device status from lights service (only for enabled devices)
        device_statuses = await self._lights.test_individual_connectivity(enabled_wiz_ips)
        
        # Update each WiZ device based on its individual status
        for device in self._devices.values():
            if device.device_type == DeviceType.WIZ:
                if not device.enabled:
                    # Disabled devices are marked as offline without checking
                    device.status = DeviceStatus.OFFLINE
                else:
                    # Check if this device's IP is in the status map
                    is_online = device_statuses.get(device.ip_address, False)
                    device.status = DeviceStatus.ONLINE if is_online else DeviceStatus.OFFLINE
                    device.last_seen = start if is_online else device.last_seen
                await self._history.record_device_event(device.device_id, device.status.value)
            # For Govee devices, keep existing behavior (cloud-based, different check needed)
            elif device.device_type == DeviceType.GOVEE:
                # For now, mark Govee devices as unknown since we don't check them individually
                device.status = DeviceStatus.UNKNOWN

    async def set_default_lighting(self) -> None:
        await self._lights.set_default_lighting()

    async def disable_device(self, device_id: str) -> bool:
        device = self._devices.get(device_id)
        if not device:
            return False
        device.enabled = False
        device.status = DeviceStatus.OFFLINE
        return True

    async def enable_device(self, device_id: str) -> bool:
        device = self._devices.get(device_id)
        if not device:
            return False
        device.enabled = True
        # we don't immediately mark online until next refresh
        return True
