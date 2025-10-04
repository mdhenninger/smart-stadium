"""
Smart Stadium WebSocket Manager
Advanced real-time communication for live game monitoring and celebration streaming
"""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
import logging

from models import (
    WebSocketMessage, CelebrationEvent, DeviceEvent, TeamEvent,
    CelebrationType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        # Subscription filters per connection
        self.subscriptions: Dict[str, List[str]] = {}
        
    async def connect(self, websocket: WebSocket, connection_id: str, client_info: Dict[str, Any] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "connected_at": datetime.now().isoformat(),
            "client_info": client_info or {},
            "message_count": 0,
            "last_activity": datetime.now().isoformat()
        }
        # Default subscriptions - all events
        self.subscriptions[connection_id] = ["all"]
        
        logger.info(f"WebSocket connected: {connection_id} (Total: {len(self.active_connections)})")
        
        # Send welcome message
        welcome_message = WebSocketMessage(
            type="connection_established",
            data={
                "connection_id": connection_id,
                "message": "Connected to Smart Stadium API",
                "available_subscriptions": [
                    "celebrations", "devices", "teams", "system_status", "all"
                ]
            },
            timestamp=datetime.now().isoformat()
        )
        await self.send_personal_message(welcome_message, connection_id)
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]
        if connection_id in self.subscriptions:
            del self.subscriptions[connection_id]
            
        logger.info(f"WebSocket disconnected: {connection_id} (Remaining: {len(self.active_connections)})")
    
    async def send_personal_message(self, message: WebSocketMessage, connection_id: str):
        """Send message to a specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(message.model_dump_json())
                
                # Update metadata
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["message_count"] += 1
                    self.connection_metadata[connection_id]["last_activity"] = datetime.now().isoformat()
                    
            except Exception as e:
                logger.warning(f"Failed to send message to {connection_id}: {e}")
                # Remove dead connection
                self.disconnect(connection_id)
    
    async def broadcast(self, message: WebSocketMessage, subscription_filter: str = "all"):
        """Broadcast message to all subscribed connections"""
        if not self.active_connections:
            return
            
        disconnected_connections = []
        message_json = message.model_dump_json()
        
        for connection_id, websocket in self.active_connections.items():
            # Check if connection is subscribed to this type of message
            user_subscriptions = self.subscriptions.get(connection_id, ["all"])
            if subscription_filter not in user_subscriptions and "all" not in user_subscriptions:
                continue
                
            try:
                await websocket.send_text(message_json)
                
                # Update metadata
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["message_count"] += 1
                    self.connection_metadata[connection_id]["last_activity"] = datetime.now().isoformat()
                    
            except Exception as e:
                logger.warning(f"Failed to broadcast to {connection_id}: {e}")
                disconnected_connections.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected_connections:
            self.disconnect(connection_id)
        
        if disconnected_connections:
            logger.info(f"Cleaned up {len(disconnected_connections)} dead connections")
    
    async def update_subscriptions(self, connection_id: str, subscriptions: List[str]):
        """Update subscription filters for a connection"""
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id] = subscriptions
            
            response = WebSocketMessage(
                type="subscription_updated",
                data={
                    "connection_id": connection_id,
                    "subscriptions": subscriptions,
                    "message": f"Subscribed to: {', '.join(subscriptions)}"
                },
                timestamp=datetime.now().isoformat()
            )
            await self.send_personal_message(response, connection_id)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about active connections"""
        total_messages = sum(
            meta.get("message_count", 0) 
            for meta in self.connection_metadata.values()
        )
        
        return {
            "total_connections": len(self.active_connections),
            "total_messages_sent": total_messages,
            "connections": {
                conn_id: {
                    "connected_duration": self._calculate_duration(meta["connected_at"]),
                    "message_count": meta.get("message_count", 0),
                    "subscriptions": self.subscriptions.get(conn_id, []),
                    "client_info": meta.get("client_info", {})
                }
                for conn_id, meta in self.connection_metadata.items()
            }
        }
    
    def _calculate_duration(self, connected_at: str) -> str:
        """Calculate connection duration"""
        try:
            connected_time = datetime.fromisoformat(connected_at)
            duration = datetime.now() - connected_time
            return str(duration).split('.')[0]  # Remove microseconds
        except:
            return "Unknown"

# Global connection manager instance
connection_manager = ConnectionManager()

class CelebrationBroadcaster:
    """Handles real-time celebration event broadcasting"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def broadcast_celebration_start(self, celebration_type: CelebrationType, team_name: str, duration: int, devices_count: int):
        """Broadcast when a celebration starts"""
        event = CelebrationEvent(
            event_type="celebration_started",
            celebration_type=celebration_type,
            team_name=team_name,
            devices_count=devices_count,
            timestamp=datetime.now().isoformat()
        )
        
        message = WebSocketMessage(
            type="celebration_event",
            data=event.model_dump(),
            timestamp=datetime.now().isoformat()
        )
        
        await self.connection_manager.broadcast(message, "celebrations")
        logger.info(f"Broadcasted celebration start: {celebration_type.value} for {team_name}")
    
    async def broadcast_celebration_progress(self, celebration_type: CelebrationType, team_name: str, progress: int, devices_count: int):
        """Broadcast celebration progress updates"""
        event = CelebrationEvent(
            event_type="celebration_progress",
            celebration_type=celebration_type,
            team_name=team_name,
            progress=progress,
            devices_count=devices_count,
            timestamp=datetime.now().isoformat()
        )
        
        message = WebSocketMessage(
            type="celebration_event",
            data=event.model_dump(),
            timestamp=datetime.now().isoformat()
        )
        
        await self.connection_manager.broadcast(message, "celebrations")
    
    async def broadcast_celebration_end(self, celebration_type: CelebrationType, team_name: str, devices_count: int):
        """Broadcast when a celebration ends"""
        event = CelebrationEvent(
            event_type="celebration_ended",
            celebration_type=celebration_type,
            team_name=team_name,
            devices_count=devices_count,
            timestamp=datetime.now().isoformat()
        )
        
        message = WebSocketMessage(
            type="celebration_event",
            data=event.model_dump(),
            timestamp=datetime.now().isoformat()
        )
        
        await self.connection_manager.broadcast(message, "celebrations")
        logger.info(f"Broadcasted celebration end: {celebration_type.value} for {team_name}")

class DeviceBroadcaster:
    """Handles real-time device event broadcasting"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def broadcast_device_status_change(self, device_id: str, device_name: str, old_status: str, new_status: str):
        """Broadcast when a device status changes"""
        from models import DeviceStatus
        
        event_type = f"device_{new_status.lower()}"
        
        event = DeviceEvent(
            event_type=event_type,
            device_id=device_id,
            device_name=device_name,
            status=DeviceStatus(new_status.lower()),
            timestamp=datetime.now().isoformat()
        )
        
        message = WebSocketMessage(
            type="device_event",
            data=event.model_dump(),
            timestamp=datetime.now().isoformat()
        )
        
        await self.connection_manager.broadcast(message, "devices")
        logger.info(f"Broadcasted device status change: {device_name} {old_status} -> {new_status}")
    
    async def broadcast_device_added(self, device_id: str, device_name: str):
        """Broadcast when a new device is added"""
        from models import DeviceStatus
        
        event = DeviceEvent(
            event_type="device_added",
            device_id=device_id,
            device_name=device_name,
            status=DeviceStatus.UNKNOWN,
            timestamp=datetime.now().isoformat()
        )
        
        message = WebSocketMessage(
            type="device_event",
            data=event.model_dump(),
            timestamp=datetime.now().isoformat()
        )
        
        await self.connection_manager.broadcast(message, "devices")
        logger.info(f"Broadcasted device added: {device_name}")

class TeamBroadcaster:
    """Handles real-time team event broadcasting"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def broadcast_team_change(self, old_team_id: Optional[str], new_team_id: str, team_name: str):
        """Broadcast when the active team changes"""
        event = TeamEvent(
            event_type="team_changed",
            old_team_id=old_team_id,
            new_team_id=new_team_id,
            team_name=team_name,
            timestamp=datetime.now().isoformat()
        )
        
        message = WebSocketMessage(
            type="team_event",
            data=event.model_dump(),
            timestamp=datetime.now().isoformat()
        )
        
        await self.connection_manager.broadcast(message, "teams")
        logger.info(f"Broadcasted team change: {old_team_id} -> {new_team_id} ({team_name})")

class SystemBroadcaster:
    """Handles system status broadcasting"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.last_status_broadcast = 0
        self.status_broadcast_interval = 30  # Broadcast system status every 30 seconds
    
    async def broadcast_system_status(self, status_data: Dict[str, Any], force: bool = False):
        """Broadcast system status updates"""
        current_time = time.time()
        
        # Only broadcast periodically unless forced
        if not force and (current_time - self.last_status_broadcast) < self.status_broadcast_interval:
            return
        
        message = WebSocketMessage(
            type="system_status",
            data=status_data,
            timestamp=datetime.now().isoformat()
        )
        
        await self.connection_manager.broadcast(message, "system_status")
        self.last_status_broadcast = current_time
        logger.debug("Broadcasted system status update")

# Global broadcaster instances
celebration_broadcaster = CelebrationBroadcaster(connection_manager)
device_broadcaster = DeviceBroadcaster(connection_manager)
team_broadcaster = TeamBroadcaster(connection_manager)
system_broadcaster = SystemBroadcaster(connection_manager)