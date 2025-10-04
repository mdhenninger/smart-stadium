"""Allow running the app module directly with python -m app."""

import uvicorn

from app.main import create_app


if __name__ == "__main__":
    uvicorn.run(
        "app.main:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
