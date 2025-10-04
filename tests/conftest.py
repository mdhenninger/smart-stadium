"""Shared pytest fixtures for Smart Stadium tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncIterator

import pytest
from httpx import AsyncClient

import pytest_asyncio

from app.config.settings import Settings
from app.main import create_app


class StubLightsService:
    """Minimal lights service stub used during tests to avoid hardware calls."""

    def __init__(self, light_ips):
        self.light_ips = list(light_ips) or ["127.0.0.1"]

    async def test_connectivity(self) -> bool:  # pragma: no cover - trivial
        return True

    def set_team_colors(self, *args, **kwargs) -> None:  # pragma: no cover - noop
        return None

    def __getattr__(self, name):  # pragma: no cover - noop proxy for async methods
        async def _async_noop(*args, **kwargs):
            return None

        return _async_noop


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """Create isolated settings pointing at ephemeral config/data directories."""

    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    sample_stadium = {
        "devices": {
            "smart_lights": {
                "ips": ["10.0.0.10"],
            }
        },
        "monitoring": {
            "sports_enabled": {"nfl": False, "college_football": False},
            "favorite_teams": {"nfl": ["BUF"], "college_football": []},
        },
    }

    sample_colors = {
        "BUF": {
            "primary": [0, 51, 141],
            "secondary": [198, 12, 48],
        }
    }

    sample_celebrations = {
        "touchdown": {"duration": 30},
    }

    sample_wiz = {
        "devices": [
            {
                "ip": "10.0.0.10",
                "name": "Test Light",
                "location": "Lab",
                "enabled": True,
            }
        ]
    }

    (config_dir / "stadium_config.json").write_text(json.dumps(sample_stadium), encoding="utf-8")
    (config_dir / "team_colors.json").write_text(json.dumps(sample_colors), encoding="utf-8")
    (config_dir / "celebrations.json").write_text(json.dumps(sample_celebrations), encoding="utf-8")
    (config_dir / "wiz_lights_config.json").write_text(json.dumps(sample_wiz), encoding="utf-8")

    settings = Settings(
        environment="test",
        root_dir=tmp_path,
        config_dir=config_dir,
        data_dir=tmp_path / "data",
        logs_dir=tmp_path / "logs",
        nfl_poll_interval=1,
        cfb_poll_interval=1,
        enable_reload=False,
    )
    settings.resolve_paths()
    return settings


@pytest_asyncio.fixture
async def app(settings: Settings, monkeypatch: pytest.MonkeyPatch):
    """Create a FastAPI app instance with patched services for testing."""

    monkeypatch.setattr("app.services.lights_service.LightsService", StubLightsService)

    application = create_app(settings)
    async with application.router.lifespan_context(application):
        yield application


@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://testserver") as async_client:
        yield async_client
