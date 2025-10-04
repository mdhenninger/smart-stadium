# Legacy API Backend (DEPRECATED)

**⚠️ THIS BACKEND IS DEPRECATED AND DISABLED ⚠️**

## Status
This API implementation has been **replaced** by the new backend in `app/`.

- **File**: `main.py.disabled` (formerly `main.py`)
- **Reason**: Routes incompatible with frontend dashboard
- **Replacement**: Use `python -m app` or `uvicorn app.main:create_app --factory`

## Why Disabled?
The frontend dashboard (`dashboard/`) expects:
- `/api/status/` (with trailing slash)
- `/api/games/live?sport=nfl`

This backend provided:
- `/api/status` (no trailing slash)
- Different route structure

## Migration Notes
- Config files in `api/config/` may need migration to `app/config/`
- Routers in `api/routers/` contain logic that may be useful for `app/api/routes/`
- WebSocket manager in `api/websocket_manager.py` has patterns worth reviewing

## If You Need to Re-enable (Emergency Only)
```bash
cd api
Rename-Item -Path "main.py.disabled" -NewName "main.py"
uvicorn api.main:app --port 8000
```

**But note**: Frontend will NOT work correctly with this backend.

## Date Disabled
October 3, 2025

## See Also
- New backend: `app/main.py`
- Architecture docs: `docs/` (if exists)
