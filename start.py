#!/usr/bin/env python3
"""
Smart Stadium - Modern Entry Point

Simple launcher for the Smart Stadium FastAPI backend.

Usage:
    python start.py                    # Start with default settings
    python start.py --reload           # Start with auto-reload (development)
    python start.py --port 8080        # Start on custom port
    python start.py --help             # Show all options

The backend will be available at: http://localhost:8000
Dashboard (frontend) runs separately: cd dashboard && npm run dev
"""

import sys
import argparse
from pathlib import Path

# Ensure we can import from app/
sys.path.insert(0, str(Path(__file__).parent))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Smart Stadium Backend Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py                    Start the backend server
  python start.py --reload           Start with auto-reload (dev mode)
  python start.py --port 8080        Start on custom port
  python start.py --host 0.0.0.0     Allow external connections

The modern architecture uses:
  - Backend:  python start.py (or: python -m app)
  - Frontend: cd dashboard && npm run dev
  - Docs:     http://localhost:8000/docs (auto-generated)
        """
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1, use 0.0.0.0 for external access)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind to (default: 8000)'
    )
    
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload for development'
    )
    
    parser.add_argument(
        '--log-level',
        default='info',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='Log level (default: info)'
    )
    
    return parser.parse_args()


def main():
    """Start the Smart Stadium backend server."""
    args = parse_args()
    
    print("🏟️  SMART STADIUM 🏟️")
    print("=" * 60)
    print("Starting modern FastAPI backend...")
    print(f"Server: http://{args.host}:{args.port}")
    print(f"Docs:   http://{args.host}:{args.port}/docs")
    print(f"Mode:   {'Development (auto-reload)' if args.reload else 'Production'}")
    print("=" * 60)
    print()
    print("💡 Tip: Run 'cd dashboard && npm run dev' in another terminal")
    print("    to start the React frontend dashboard.")
    print()
    
    try:
        import uvicorn
        
        # Use the factory pattern from app/main.py
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            access_log=True,
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
    except ImportError:
        print("❌ Error: uvicorn not installed")
        print("Install with: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
