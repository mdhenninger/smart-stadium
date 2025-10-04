"""History endpoints for celebrations, device events, and errors."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_container
from app.models.api import ApiResponse

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("/celebrations", response_model=ApiResponse)
async def recent_celebrations(limit: int = Query(50, le=200), container=Depends(get_container)):
    records = await container.history_store.recent_celebrations(limit)
    return ApiResponse(success=True, data={"celebrations": records})


@router.get("/devices", response_model=ApiResponse)
async def recent_device_events(limit: int = Query(50, le=200), container=Depends(get_container)):
    records = await container.history_store.recent_device_events(limit)
    return ApiResponse(success=True, data={"device_events": records})


@router.get("/errors", response_model=ApiResponse)
async def recent_errors(limit: int = Query(50, le=200), container=Depends(get_container)):
    records = await container.history_store.recent_errors(limit)
    return ApiResponse(success=True, data={"errors": records})
