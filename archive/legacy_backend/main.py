"""
Smart Stadium API - Main FastAPI Application
Real-time celebration control and device management
"""

import asyncio
import time
import os
import sys
import uuid
import json
from datetime import datetime
from typing import List

# Add Smart Stadium src directory to path for imports
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uuid

# Local imports with absolute paths
sys.path.insert(0, os.path.dirname(__file__))

from models import (
    ApiResponse, SystemStatus, CelebrationRequest, TeamChangeRequest,
    WebSocketMessage, CelebrationEvent, DeviceEvent, TeamEvent
)

# Import routers (we'll create these next)
from routers import celebrations, devices, teams, games, dashboard

# Import WebSocket manager
from websocket_manager import (
    connection_manager, celebration_broadcaster, device_broadcaster, 
    team_broadcaster, system_broadcaster
)

# Import live game monitor
from live_game_monitor import live_monitor

# Import Smart Stadium components
try:
    # Add parent directory to path for Smart Stadium modules
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    src_path = os.path.join(parent_dir, 'src')
    sys.path.insert(0, src_path)
    
    from device_manager import SmartDeviceManager
    from smart_lights import BillsCelebrationController as SmartStadiumLights
    from game_monitor import SmartStadiumGameMonitor
    SMART_STADIUM_AVAILABLE = True
    print("✅ Smart Stadium components loaded successfully")
except ImportError as e:
    print(f"⚠️ Smart Stadium components not available: {e}")
    SmartStadiumLights = None
    SmartDeviceManager = None
    SmartStadiumGameMonitor = None
    SMART_STADIUM_AVAILABLE = False

class SmartStadiumAPI:
    """Main API class that manages the Smart Stadium system"""
    
    def __init__(self):
        self.start_time = time.time()
        self.device_manager = None
        self.stadium_lights = None
        self.current_celebration = None
        
        # Expose broadcasters for router access
        self.celebration_broadcaster = celebration_broadcaster
        self.device_broadcaster = device_broadcaster
        self.team_broadcaster = team_broadcaster
        self.system_broadcaster = system_broadcaster
        
        # Initialize live monitor with stadium API reference
        live_monitor.stadium_api = self
        
    async def initialize(self):
        """Initialize the Smart Stadium system"""
        try:
            if not SMART_STADIUM_AVAILABLE:
                print("⚠️ Smart Stadium components not available - running in API-only mode")
                return False
                
            print("🏟️ Initializing Smart Stadium API...")
            
            # Initialize Smart Stadium (it will create its own device manager)
            self.stadium_lights = SmartStadiumLights()
            
            # Get reference to the device manager from SmartStadiumLights
            self.device_manager = self.stadium_lights.device_manager
            
            print("✅ Smart Stadium API initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Smart Stadium API: {e}")
            return False
    
    async def broadcast_to_websockets(self, message: WebSocketMessage):
        """Broadcast message to all connected WebSocket clients - deprecated, use broadcasters"""
        await connection_manager.broadcast(message)
    
    async def get_system_status(self) -> SystemStatus:
        """Get current system status"""
        if not SMART_STADIUM_AVAILABLE:
            # Return mock data when Smart Stadium not available
            from models import Team
            mock_team = Team(
                id="NFL-BUFFALO-BILLS",
                league="NFL",
                city="Buffalo",
                name="Bills",
                full_name="Buffalo Bills",
                primary_color=(0, 0, 255),
                secondary_color=(255, 0, 0)
            )
            return SystemStatus(
                total_devices=0,
                online_devices=0,
                offline_devices=0,
                current_team=mock_team,
                red_zone_active=False,
                uptime_seconds=time.time() - self.start_time
            )
            
        if not self.device_manager or not self.stadium_lights:
            raise HTTPException(status_code=503, detail="Smart Stadium not initialized")
        
        # Get device status
        device_status = await self.device_manager.get_device_status_summary()
        
        # Get current team
        current_team_data = self.stadium_lights.get_current_team_info()
        
        return SystemStatus(
            total_devices=device_status["total"],
            online_devices=device_status["online"],
            offline_devices=device_status["offline"],
            current_team=current_team_data,
            red_zone_active=getattr(self.stadium_lights, 'red_zone_active', False),
            uptime_seconds=time.time() - self.start_time
        )

# Create global API instance
stadium_api = SmartStadiumAPI()

# Create FastAPI app with enhanced security
app = FastAPI(
    title="Smart Stadium API",
    description="Real-time football celebration control and smart device management",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=[
        "localhost", 
        "127.0.0.1", 
        "0.0.0.0",
        # Add your production domains:
        # "yourdomain.com",
        # "api.yourdomain.com"
    ]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Generate request ID for tracking
    request_id = str(uuid.uuid4())
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self' ws: wss:"
    )
    
    # API headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-API-Version"] = "1.0.0"
    response.headers["X-Response-Time"] = str(int((time.time() - request.state.start_time) * 1000)) + "ms" if hasattr(request.state, 'start_time') else "unknown"
    
    return response

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Track request processing time"""
    start_time = time.time()
    request.state.start_time = start_time
    response = await call_next(request)
    return response

# Configure CORS with security-conscious settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:3001",  # Alternative React port
        "http://127.0.0.1:3000",  # Local development
        "http://127.0.0.1:3001",  # Alternative local port
        # Add your production domains here:
        # "https://yourdomain.com",
        # "https://dashboard.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-Client-ID",
        "X-Request-ID"
    ],
    expose_headers=[
        "X-Request-ID",
        "X-Response-Time",
        "X-API-Version"
    ]
)

# Include routers
app.include_router(celebrations.router, prefix="/api/celebrations", tags=["Celebrations"])
app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])  
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
app.include_router(games.router, tags=["Games"])
app.include_router(dashboard.router, tags=["Dashboard"])

@app.on_event("startup")
async def startup_event():
    """Initialize Smart Stadium on startup"""
    success = await stadium_api.initialize()
    if not success:
        print("⚠️ Smart Stadium initialization failed - API running in limited mode")
    
    # Initialize live game monitor
    try:
        await live_monitor.initialize()
        print("🎮 Live Game Monitor initialized successfully!")
    except Exception as e:
        print(f"⚠️ Live Game Monitor initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        await live_monitor.stop_monitoring()
        print("🛑 Live Game Monitor stopped")
    except Exception as e:
        print(f"⚠️ Error stopping Live Game Monitor: {e}")

@app.get("/api/status", response_model=SystemStatus)
async def get_status():
    """Get system status and health check"""
    try:
        return await stadium_api.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return ApiResponse(
        success=True,
        message="Smart Stadium API is running",
        data={
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - stadium_api.start_time
        }
    )

@app.get("/api/websockets/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    stats = connection_manager.get_connection_stats()
    return ApiResponse(
        success=True,
        message="WebSocket connection statistics",
        data=stats
    )

@app.websocket("/api/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str = Query(None, description="Optional client identifier"),
    subscriptions: str = Query("all", description="Comma-separated list of subscriptions")
):
    """Enhanced WebSocket endpoint for real-time updates"""
    
    # Generate unique connection ID
    connection_id = client_id or f"client_{uuid.uuid4().hex[:8]}"
    
    # Parse subscriptions
    subscription_list = [s.strip() for s in subscriptions.split(",") if s.strip()]
    
    # Client info for tracking
    client_info = {
        "user_agent": websocket.headers.get("user-agent", "Unknown"),
        "subscriptions": subscription_list,
        "connection_type": "websocket"
    }
    
    try:
        # Connect with enhanced manager
        await connection_manager.connect(websocket, connection_id, client_info)
        
        # Update subscriptions if specified
        if subscription_list and subscription_list != ["all"]:
            await connection_manager.update_subscriptions(connection_id, subscription_list)
        
        # Send initial system status
        try:
            status = await stadium_api.get_system_status()
            status_message = WebSocketMessage(
                type="initial_system_status",
                data=status.model_dump(),
                timestamp=datetime.now().isoformat()
            )
            await connection_manager.send_personal_message(status_message, connection_id)
        except Exception as e:
            print(f"⚠️ Could not send initial status: {e}")
        
        # Handle incoming messages
        while True:
            try:
                message_text = await websocket.receive_text()
                await handle_websocket_message(message_text, connection_id, websocket)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket message error: {e}")
                error_message = WebSocketMessage(
                    type="error",
                    data={"error": str(e), "message": "Message processing failed"},
                    timestamp=datetime.now().isoformat()
                )
                await connection_manager.send_personal_message(error_message, connection_id)
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        # Clean up connection
        connection_manager.disconnect(connection_id)

async def handle_websocket_message(message_text: str, connection_id: str, websocket: WebSocket):
    """Enhanced WebSocket message handling with comprehensive features"""
    try:
        message_data = json.loads(message_text)
        message_type = message_data.get("type", "unknown")
        
        if message_type == "ping":
            # Respond to ping with pong for heartbeat
            pong_message = WebSocketMessage(
                type="pong",
                data={
                    "timestamp": datetime.now().isoformat(),
                    "connection_id": connection_id,
                    "server_time": datetime.now().isoformat()
                },
                timestamp=datetime.now().isoformat()
            )
            await connection_manager.send_personal_message(pong_message, connection_id)
            
        elif message_type == "subscribe" or message_data.get("action") == "subscribe":
            # Update subscriptions
            new_subscriptions = message_data.get("subscriptions", ["all"])
            await connection_manager.update_subscriptions(connection_id, new_subscriptions)
            
        elif message_type == "get_status":
            # Send current system status
            try:
                status = await stadium_api.get_system_status()
                status_message = WebSocketMessage(
                    type="system_status",
                    data=status.model_dump(),
                    timestamp=datetime.now().isoformat()
                )
                await connection_manager.send_personal_message(status_message, connection_id)
            except Exception as e:
                error_message = WebSocketMessage(
                    type="error",
                    data={"error": f"Failed to get system status: {str(e)}"},
                    timestamp=datetime.now().isoformat()
                )
                await connection_manager.send_personal_message(error_message, connection_id)
            
        elif message_type == "get_connection_stats":
            # Send connection statistics (admin feature)
            stats = connection_manager.get_connection_stats()
            stats_message = WebSocketMessage(
                type="connection_stats",
                data=stats,
                timestamp=datetime.now().isoformat()
            )
            await connection_manager.send_personal_message(stats_message, connection_id)
            
        elif message_data.get("action") == "subscribe_game":
            # Subscribe to specific game updates
            game_id = message_data.get("game_id")
            if game_id:
                # TODO: Implement game-specific subscriptions
                response = WebSocketMessage(
                    type="subscription_confirmed",
                    data={
                        "subscription_type": "game",
                        "game_id": game_id,
                        "message": f"Subscribed to game {game_id}"
                    },
                    timestamp=datetime.now().isoformat()
                )
                await connection_manager.send_personal_message(response, connection_id)
                
        elif message_data.get("action") == "subscribe_devices":
            # Subscribe to device updates
            device_ids = message_data.get("device_ids", [])
            response = WebSocketMessage(
                type="subscription_confirmed",
                data={
                    "subscription_type": "devices",
                    "device_ids": device_ids,
                    "message": f"Subscribed to {len(device_ids)} devices"
                },
                timestamp=datetime.now().isoformat()
            )
            await connection_manager.send_personal_message(response, connection_id)
            
        elif message_data.get("action") == "subscribe_celebrations":
            # Subscribe to celebration updates
            response = WebSocketMessage(
                type="subscription_confirmed", 
                data={
                    "subscription_type": "celebrations",
                    "message": "Subscribed to celebration updates"
                },
                timestamp=datetime.now().isoformat()
            )
            await connection_manager.send_personal_message(response, connection_id)
            
        elif message_type == "client_info":
            # Update client information
            client_info = message_data.get("data", {})
            if connection_id in connection_manager.connection_metadata:
                connection_manager.connection_metadata[connection_id]["client_info"].update(client_info)
                
        else:
            # Unknown message type
            print(f"Unknown WebSocket message type: {message_type} from {connection_id}")
            error_message = WebSocketMessage(
                type="error",
                data={
                    "error": f"Unknown message type: {message_type}",
                    "supported_types": ["ping", "subscribe", "get_status", "get_connection_stats"]
                },
                timestamp=datetime.now().isoformat()
            )
            await connection_manager.send_personal_message(error_message, connection_id)
            
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in WebSocket message from {connection_id}: {e}")
        error_message = WebSocketMessage(
            type="error",
            data={"error": "Invalid JSON format", "details": str(e)},
            timestamp=datetime.now().isoformat()
        )
        await connection_manager.send_personal_message(error_message, connection_id)
        
    except Exception as e:
        print(f"Error handling WebSocket message from {connection_id}: {e}")
        error_message = WebSocketMessage(
            type="error",
            data={"error": "Message processing failed", "details": str(e)},
            timestamp=datetime.now().isoformat()
        )
        await connection_manager.send_personal_message(error_message, connection_id)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Smart Stadium API Server...")
    print("📊 API Documentation: http://localhost:8000/api/docs")
    print("🔌 WebSocket Endpoint: ws://localhost:8000/api/ws")
    print("💡 Health Check: http://localhost:8000/api/health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["api", "src"],
        log_level="info"
    )