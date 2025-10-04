# API Directory

**Note:** The legacy backend implementation that was previously in this directory has been **archived** as of October 4, 2025.

## Current Status

✅ **Active Backend:** `app/` directory (modern implementation)
📦 **Archived Code:** `archive/legacy_backend/` (reference only)

## What Happened?

The legacy FastAPI backend (`main.py.disabled`, `routers/`, `models.py`, etc.) has been moved to `archive/legacy_backend/` to:
1. Eliminate confusion about which backend to use
2. Clean up dual-architecture setup
3. Maintain single source of truth for API implementation

## What Remains Here?

This directory now contains only:
- `__init__.py` - Package marker
- `README.md` - This file
- `__pycache__/` - Python cache files

**These minimal files allow `app/` to import from `api/` namespace if needed, but the legacy backend code is archived.**

## Where Did Everything Go?

| Old Location | New Location | Purpose |
|--------------|--------------|---------|
| `api/main.py.disabled` | `archive/legacy_backend/main.py` | Legacy FastAPI app (541 lines) |
| `api/routers/` | `archive/legacy_backend/routers/` | 5 legacy route modules |
| `api/models.py` | `archive/legacy_backend/models.py` | Legacy Pydantic models |
| `api/espn_service.py` | `archive/legacy_backend/espn_service.py` | Legacy ESPN integration |
| `api/websocket_manager.py` | `archive/legacy_backend/websocket_manager.py` | Legacy WebSocket handler |
| `api/live_game_monitor.py` | `archive/legacy_backend/live_game_monitor.py` | Legacy game monitor |
| `api/test_*.py` | `archive/legacy_backend/test_*.py` | Legacy test files |

## Active Backend

**Use the modern implementation:**
```bash
# Start the backend
python -m app

# Or with uvicorn directly
uvicorn app.main:app --reload
```

**Modern structure:**
- `app/main.py` - FastAPI factory with lifespan management
- `app/api/routes/` - Clean route modules (6 routers)
- `app/core/` - Service container & dependency injection
- `app/models/` - Modern Pydantic models
- `app/services/` - Business logic services

## Documentation

- **Archive Details:** See `archive/README.md`
- **Risk Analysis:** See `BACKEND_INTEGRATION_RISKS.md`
- **Current State:** See `CURRENT_STATE.md`

## Need the Old Code?

**For reference only:** Check `archive/legacy_backend/`

**Rollback instructions** (emergency only) are in `archive/README.md`

**But note**: Frontend will NOT work correctly with this backend.

## Date Disabled
October 3, 2025

## See Also
- New backend: `app/main.py`
- Architecture docs: `docs/` (if exists)
