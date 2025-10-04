"""Simple WebSocket connection manager."""

from __future__ import annotations

from typing import Dict, Set

from fastapi import WebSocket
from app.utils.logging import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self._connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self._connections)}")

    async def broadcast(self, message: dict) -> None:
        if not self._connections:
            logger.debug("No WebSocket connections to broadcast to")
            return
            
        dead = []
        successful = 0
        for connection in self._connections:
            try:
                await connection.send_json(message)
                successful += 1
            except Exception as exc:
                logger.warning(f"Failed to send message to WebSocket: {exc}")
                dead.append(connection)
        
        for connection in dead:
            self.disconnect(connection)
        
        logger.debug(f"Broadcast message to {successful}/{len(self._connections) + len(dead)} connections")
