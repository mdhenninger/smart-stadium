"""System status endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request

from app.dependencies import get_container, get_app_state
from app.models.api import SystemStatusResponse

router = APIRouter(prefix="/api/status", tags=["Status"])


@router.get("/", response_model=SystemStatusResponse)
async def get_system_status(request: Request, container=Depends(get_container)):
    state = request.app.state.app_state
    uptime = (datetime.now(timezone.utc) - state.start_time).total_seconds()
    device_summary = container.device_manager.summary()
    return SystemStatusResponse(
        uptime_seconds=uptime,
        environment=state.settings.environment,
        total_devices=device_summary.total_devices,
        enabled_devices=device_summary.enabled_devices,
        online_devices=device_summary.online_devices,
        offline_devices=device_summary.offline_devices,
        monitoring_active=True,
        sports_enabled=container.config.get_sports_enabled(),
    )
