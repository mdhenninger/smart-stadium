# Archive Directory

This directory contains legacy code that has been replaced by modern implementations but preserved for reference.

## Purpose

Code is archived rather than deleted to:
1. **Preserve History** - Maintain reference to previous architectural decisions
2. **Enable Rollback** - Quick recovery if issues arise with modern implementations
3. **Aid Migration** - Help understand what functionality was replaced and how
4. **Document Evolution** - Show the project's architectural progression

## Contents

### `legacy_backend/` - Original FastAPI Backend (Archived October 4, 2025)

**Why Archived:**
- Dual backend architecture caused confusion (two ways to start the system)
- Modern `app/` backend supersedes this implementation with cleaner architecture
- Risk analysis confirmed frontend exclusively uses modern backend
- No breaking changes from archival (validated via testing)

**Original Location:** `api/` folder (root level)

**Key Components Archived:**
- `main.py` - Legacy FastAPI application (541 lines)
  - Direct imports from `src/` directory
  - Monolithic structure with inline route definitions
  - Competed with modern app for port 8000
  
- `routers/` - Legacy route modules
  - `celebrations.py` - Celebration triggers (282 lines)
  - `devices.py` - Device management (301 lines)
  - `dashboard.py` - Dashboard bundle endpoints (394 lines) ⚠️ Not used by frontend
  - `games.py` - Live game data
  - `teams.py` - Team information
  
- `models.py` - Pydantic models for legacy API
- `espn_service.py` - ESPN API integration (legacy version)
- `websocket_manager.py` - WebSocket connection manager (legacy)
- `live_game_monitor.py` - Game monitoring service (legacy)
- `start_server.py` - Legacy server launcher
- `test_*.py` - Legacy test files

**Modern Replacement:** `app/` directory structure
- `app/main.py` - Modern FastAPI factory with lifespan management
- `app/api/routes/` - Clean route modules (6 routers)
- `app/core/` - Service container with dependency injection
- `app/models/` - Modern Pydantic models
- `app/services/` - Business logic services

**Key Differences:**
| Aspect | Legacy (`api/`) | Modern (`app/`) |
|--------|----------------|-----------------|
| Architecture | Monolithic | Modular with DI |
| Startup | Direct execution | Factory pattern |
| Services | Global instances | Container-managed |
| Routes | Some inline | All in `api/routes/` |
| Config | Mixed sources | Centralized |
| Entry Point | Multiple scripts | `python -m app` |

**Migration Notes:**
- Frontend validated working with modern backend
- All 6 modern routers match frontend expectations
- WebSocket endpoint migrated: `/api/ws` (same path)
- Data models aligned (TypeScript ↔ Pydantic)
- Dashboard router endpoints (`/api/dashboard/*`) not used by frontend

**Documentation:**
- See `BACKEND_INTEGRATION_RISKS.md` for detailed risk analysis
- See `CURRENT_STATE.md` for pre-archival system state
- See `FIXES_APPLIED.md` for recent bug fixes

**Rollback Instructions:**
If you need to restore legacy backend:
```bash
# Restore files from archive
cp -r archive/legacy_backend/* api/

# Rename main file
mv api/main.py api/main.py.disabled
mv api/main.py.disabled api/main.py

# Change modern app port in app/config/settings.py
# Update frontend proxy in dashboard/vite.config.ts
```

**Status:** ✅ Safe to reference, not for active use

---

## Guidelines for Adding to Archive

When archiving code:

1. **Document thoroughly** - Explain what, why, when
2. **Preserve context** - Include relevant documentation
3. **Note replacements** - Link to modern equivalent
4. **Test first** - Validate modern implementation works
5. **Git commit** - Ensure rollback capability
6. **Update docs** - Remove references to archived code from active documentation

## Maintenance Policy

- **Keep:** Reference for understanding architectural evolution
- **Review:** Annually to determine if still needed
- **Delete:** After 2+ years if modern implementation proven stable

---

**Last Updated:** October 4, 2025
**Maintained By:** Smart Stadium Development Team
