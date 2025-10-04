from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_status_endpoint(client):
    response = await client.get("/api/status/")
    assert response.status_code == 200
    payload = response.json()

    assert payload["environment"] == "test"
    assert payload["monitoring_active"] is True
    assert payload["sports_enabled"] == {"nfl": False, "college_football": False}
    assert payload["total_devices"] == 1
    assert payload["enabled_devices"] == 1
