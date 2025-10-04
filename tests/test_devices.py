from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_devices_listing(client):
    response = await client.get("/api/devices/")
    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    devices = payload["data"]["devices"]
    summary = payload["data"]["summary"]

    assert len(devices) == 1
    assert devices[0]["name"] == "Test Light"
    assert summary["total_devices"] == 1
