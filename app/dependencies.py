"""FastAPI dependency helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException, Request

from app.core.container import ServiceContainer

if TYPE_CHECKING:  # pragma: no cover - import for typing only
    from app.main import AppState


def get_app_state(request: Request) -> "AppState":
    return request.app.state.app_state


def get_container(request: Request) -> ServiceContainer:
    state = get_app_state(request)
    if not state.container:
        raise HTTPException(status_code=503, detail="Service container not initialized")
    return state.container
