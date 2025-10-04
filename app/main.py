"""Smart Stadium FastAPI application factory."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime, timezone

from app.api.routes import celebrations, devices, games, history, monitoring, status, teams
from app.config.settings import Settings, load_settings
from app.core.config_manager import ConfigManager
from app.core.container import ServiceContainer, build_container
from app.utils.logging import configure_logging, get_logger
from app.websocket.manager import WebSocketManager


@dataclass(slots=True)
class AppState:
    settings: Settings
    config_manager: ConfigManager
    container: ServiceContainer | None = None
    start_time: datetime = datetime.now(timezone.utc)
    websocket_manager: WebSocketManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger = get_logger(__name__)
    state: AppState = app.state.app_state

    logger.info("Starting Smart Stadium application")
    config = state.config_manager.refresh()
    logger.info("Configuration loaded successfully")

    if state.websocket_manager is None:
        state.websocket_manager = WebSocketManager()

    state.container = build_container(state.config_manager, state.websocket_manager)
    logger.info(
        "Device manager initialized with %d devices",
        len(list(state.container.device_manager.list_devices())),
    )

    await state.container.history_store.initialize()
    await state.container.monitoring_store.initialize()
    logger.info("Monitoring store initialized")
    
    # Perform initial device status check
    await state.container.device_manager.refresh_status()
    logger.info("Initial device status check completed")
    
    # Set lights to default warm white on startup
    await state.container.lights_service.set_default_lighting()
    logger.info("Lights set to default on startup")
    
    await state.container.monitoring.start_all()
    logger.info("Monitoring services started")

    try:
        yield
    finally:
        logger.info("Shutting down Smart Stadium application")
        if state.container:
            await state.container.monitoring.stop_all()
            await state.container.lights_service.set_default_lighting()
            logger.info("Lights reset to default on shutdown")
            await state.container.scoreboard_client.close()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Application factory used by scripts and ASGI servers."""

    settings = settings or load_settings()
    configure_logging(settings.logs_dir, settings.environment)

    websocket_manager = WebSocketManager()
    config_manager = ConfigManager(settings)
    app_state = AppState(
        settings=settings,
        config_manager=config_manager,
    start_time=datetime.now(timezone.utc),
        websocket_manager=websocket_manager,
    )

    app = FastAPI(
        title="Smart Stadium API",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.state.app_state = app_state

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(status.router)
    app.include_router(devices.router)
    app.include_router(celebrations.router)
    app.include_router(games.router)
    app.include_router(history.router)
    app.include_router(teams.router)
    app.include_router(monitoring.router)

    @app.websocket("/api/ws")
    async def websocket_endpoint(websocket: WebSocket):
        state: AppState = app.state.app_state
        manager = state.websocket_manager
        if manager is None:
            await websocket.close(code=1011)
            return

        await manager.connect(websocket)
        try:
            # Keep connection alive with periodic pings
            while True:
                try:
                    # Wait for messages with timeout to send periodic pings
                    await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    try:
                        await websocket.send_json({"type": "ping"})
                    except Exception:
                        break
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception as exc:
            logger = get_logger(__name__)
            logger.error(f"WebSocket error: {exc}")
            manager.disconnect(websocket)

    return app


# Create default app instance for uvicorn
app = create_app()
