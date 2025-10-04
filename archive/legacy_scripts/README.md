# Legacy Scripts Archive

This directory contains standalone scripts and CLI tools that were replaced by the modern `app/` architecture.

## Archived: October 4, 2025

These scripts represent the evolution from standalone CLI tools to a modern FastAPI web service architecture.

---

## Entry Points (Archived)

### `bills_launcher.py`
**Purpose:** Interactive menu launcher for choosing monitoring modes  
**Replaced By:** `python start.py` (or `python -m app`)  
**Why Archived:** Modern backend handles all monitoring via API endpoints

### `src/main.py`
**Purpose:** Original CLI-based Smart Stadium entry point (72 lines)  
**Replaced By:** `app/main.py` (FastAPI factory pattern)  
**Why Archived:** Shifted from CLI to web API architecture

---

## Standalone Monitors (Archived)

### Bills-Specific Scripts
- `src/bills_celebrations.py` (579 lines) - Bills-only celebration controller
- `src/bills_score_monitor.py` - Bills game monitoring logic

**Replaced By:** `app/services/` with multi-team support via `app/models/team.py`

### NFL/CFB Monitors
- `src/enhanced_nfl_monitor.py` - Enhanced NFL game monitoring
- `src/dynamic_nfl_monitor.py` - Dynamic multi-game NFL monitoring
- `src/game_monitor.py` - Generic game monitoring base

**Replaced By:** 
- `app/services/scoreboard_service.py` - Modern ESPN integration
- `app/services/game_monitor_service.py` - Unified game monitoring
- `src/sports/nfl_monitor.py` - Still active for `app/` to use

---

## Hardware Controllers (Archived)

### `src/smart_stadium_lights.py`
**Purpose:** Original smart light controller  
**Status:** Superseded by `src/devices/smart_lights.py`  
**Note:** `src/devices/smart_lights.py` is STILL ACTIVE - it's the hardware bridge

### `src/smart_lights.py`
**Purpose:** Early version of light controller  
**Status:** Replaced by `src/devices/smart_lights.py`

### `src/device_manager.py`
**Purpose:** Original device management  
**Replaced By:** `app/core/device_manager.py` (modern version with async)

---

## Utility Scripts (Archived)

### Debugging Tools
- `debug_syracuse.py` - Syracuse game debugging
- `debug_syracuse2.py` - Follow-up debugging
- `check_db.py` - Database inspection utility
- `test_connection.py` - Connection testing tool
- `analyze_integration_safety.py` - Integration analysis tool

**Current Tools:**
- Use API endpoints for debugging: `http://localhost:8000/docs`
- Use `pytest` tests in `tests/` directory
- Modern logging in `logs/smart_stadium.log`

### Database Tools
- `src/generate_sports_database.py` - Sports database generator

**Replaced By:**
- `app/models/` - Pydantic models with validation
- `config/team_colors.json` - Centralized team data
- `migrate_team_database.py` - Still active (root level) for migrations

---

## Migration Path

**From:** Standalone CLI scripts with direct hardware control  
**To:** Modern FastAPI web service with:
- REST API endpoints (`app/api/routes/`)
- WebSocket real-time updates (`app/websocket/`)
- React dashboard frontend (`dashboard/`)
- Service-oriented architecture (`app/services/`)
- Dependency injection (`app/core/container.py`)

---

## If You Need These Scripts

### For Reference
These scripts contain valuable logic and patterns that informed the modern architecture. They're preserved for:
1. Understanding architectural evolution
2. Reference implementations
3. Historical context

### Running Legacy Scripts (Not Recommended)
If you must run a legacy script:
```bash
# From project root
python archive/legacy_scripts/bills_launcher.py

# Or
cd archive/legacy_scripts
python bills_launcher.py
```

⚠️ **Warning:** Legacy scripts may have dependency conflicts with modern `app/` code.

---

## Modern Equivalents

| Legacy Script | Modern Approach |
|---------------|-----------------|
| `bills_launcher.py` | `python start.py` |
| `src/main.py` | `python -m app` |
| `bills_celebrations.py` | `POST /api/celebrations/trigger` |
| `enhanced_nfl_monitor.py` | `GET /api/games/live?sport=nfl` |
| `check_db.py` | `GET /api/history/celebrations` |
| `test_connection.py` | `GET /api/status/` |

---

## Documentation

- **Modern Architecture:** See root `README.md`
- **API Documentation:** http://localhost:8000/docs (when backend running)
- **Current State:** See `CURRENT_STATE.md`
- **Backend Details:** See `app/README.md` (if exists)

---

**Status:** ✅ Safe to reference, not for active use  
**Last Updated:** October 4, 2025  
**Reason:** Phase 2 Consolidation - Entry Point Cleanup
