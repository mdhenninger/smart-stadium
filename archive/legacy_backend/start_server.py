"""
Smart Stadium API Startup Script
Easy way to launch the FastAPI server
"""

import os
import sys
import uvicorn

def start_api_server():
    """Start the Smart Stadium API server"""
    print("🚀 Starting Smart Stadium API Server...")
    print("=" * 50)
    print("📊 API Documentation: http://localhost:8000/api/docs")
    print("🔗 Interactive API: http://localhost:8000/api/redoc")
    print("🔌 WebSocket Endpoint: ws://localhost:8000/api/ws")
    print("💡 Health Check: http://localhost:8000/api/health")
    print("📈 System Status: http://localhost:8000/api/status")
    print("=" * 50)
    print("🏈 Ready for game day celebrations!")
    print("\n✨ Example API calls:")
    print("   POST http://localhost:8000/api/celebrations/touchdown")
    print("   POST http://localhost:8000/api/celebrations/sack")
    print("   GET  http://localhost:8000/api/teams/")
    print("   GET  http://localhost:8000/api/devices/")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Change to the API directory
    api_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(api_dir)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[api_dir, os.path.join(os.path.dirname(api_dir), 'src')],
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    start_api_server()