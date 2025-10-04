"""Device management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_container
from app.models.api import ApiResponse, DeviceToggleRequest

router = APIRouter(prefix="/api/devices", tags=["Devices"])


@router.get("/", response_model=ApiResponse)
async def list_devices(container=Depends(get_container)):
    devices = [device.model_dump() for device in container.device_manager.list_devices()]
    summary = container.device_manager.summary().model_dump()
    return ApiResponse(success=True, data={"devices": devices, "summary": summary})


@router.get("/{device_id}", response_model=ApiResponse)
async def get_device(device_id: str, container=Depends(get_container)):
    device = container.device_manager.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    return ApiResponse(success=True, data=device.model_dump())


@router.put("/{device_id}/toggle", response_model=ApiResponse)
async def toggle_device(device_id: str, payload: DeviceToggleRequest, container=Depends(get_container)):
    if payload.enabled:
        success = await container.device_manager.enable_device(device_id)
    else:
        success = await container.device_manager.disable_device(device_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    return ApiResponse(success=True, message="Device updated", data={"device_id": device_id, "enabled": payload.enabled})


@router.post("/{device_id}/test", response_model=ApiResponse)
async def test_device(device_id: str, container=Depends(get_container)):
    device = container.device_manager.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    result = await container.lights_service.test_connectivity()
    # Refresh status cache after test
    await container.device_manager.refresh_status()
    return ApiResponse(success=result, data={"device_id": device_id, "online": result})


@router.post("/default-lighting", response_model=ApiResponse)
async def set_default_lighting(container=Depends(get_container)):
    await container.device_manager.set_default_lighting()
    return ApiResponse(success=True, message="Lights set to default warm state")
