from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_history_endpoint(client):
    response = await client.get("/api/history/celebrations?limit=10")
    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["data"] == {"celebrations": []}
