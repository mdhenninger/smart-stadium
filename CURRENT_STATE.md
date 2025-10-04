# Smart Stadium - Current State Documentation

**Date:** October 4, 2025  
**Purpose:** Pre-consolidation snapshot documenting system architecture and known issues

---

## 🎯 Executive Summary

The Smart Stadium project has **two parallel backend implementations** that need consolidation:
- **Modern Backend** (`app/` folder) - Production-ready, properly structured ✅
- **Legacy Backend** (`api/` folder) - Disabled, needs archival ⚠️

The modern system is functional but hidden behind duplicate entry points and legacy code.

---

## 📊 Architecture Overview

### ✅ **Working Production System**

```
app/                              # Modern FastAPI Backend (USE THIS)
├── main.py                       # App factory with lifespan management
├── __main__.py                   # CLI entry: python -m app
├── api/routes/                   # Clean REST API structure
│   ├── celebrations.py          # POST celebration triggers
│   ├── devices.py               # Device management
│   ├── games.py                 # Live game data
│   ├── history.py               # Event history
│   ├── status.py                # System health
│   └── teams.py                 # Team data
├── core/
│   ├── config_manager.py        # Unified config loading
│   ├── container.py             # DI service container
│   └── ...
├── services/
│   ├── lights_service.py        # Hardware abstraction
│   ├── espn_client.py           # ESPN API integration
│   ├── monitoring.py            # Game monitoring coordinator
│   └── ...
├── models/                       # Pydantic data models
└── websocket/                    # Real-time updates

dashboard/                        # React + TypeScript Frontend
├── src/
│   ├── App.tsx                  # Main application
│   ├── components/              # UI components
│   ├── hooks/useLiveEvents.ts   # WebSocket integration
│   └── services/                # API clients
└── package.json                  # Node dependencies

src/devices/                      # Hardware Controllers (KEEP)
└── smart_lights.py              # Core WiZ light integration

config/                           # JSON Configuration Files
├── stadium_config.json          # Main system config
├── team_colors.json             # Team color database
├── celebrations.json            # Celebration definitions
└── wiz_lights_config.json       # Light device config
```

### ⚠️ **Legacy/Duplicate Code (NEEDS ARCHIVAL)**

```
api/                              # Old Backend (ARCHIVE)
├── main.py.disabled             # Already disabled
├── start_server.py              # Points to wrong main
├── models.py                    # Superseded by app/models/
├── websocket_manager.py         # Superseded by app/websocket/
└── routers/                     # Superseded by app/api/routes/

src/                              # Mixed CLI Scripts & Core (PARTIAL ARCHIVE)
├── main.py                      # Old controller (ARCHIVE)
├── bills_*.py                   # Legacy Bills scripts (ARCHIVE)
├── enhanced_nfl_monitor.py      # Superseded by app/services (ARCHIVE)
├── dynamic_nfl_monitor.py       # Superseded (ARCHIVE)
├── core/                        # Old controllers (ARCHIVE)
│   ├── stadium_controller.py
│   └── stadium_controller_old.py
└── sports/                      # Sport monitors (KEEP - used by app/)
    ├── nfl_monitor.py
    └── college_monitor.py

College/                          # Standalone System (DECISION NEEDED)
└── src/
    ├── college_game_monitor.py
    └── college_celebrations.py
```

---

## 🔧 **Current Issues**

### **1. Dual Backend Conflict**
- **Problem:** Both `app/` and `api/` try to serve on port 8000
- **Impact:** Confusion about which system to start
- **Status:** `api/main.py` already disabled, but folder structure remains
- **Resolution:** Archive `api/` folder → `archive/api-legacy/`

### **2. Multiple Entry Points**
Five different ways to start the system:
1. `python -m app` → ✅ Modern backend (CORRECT)
2. `api/start_server.py` → ❌ Points to disabled main
3. `src/main.py` → ❌ Old CLI controller
4. `bills_launcher.py` → ❌ Legacy Bills-specific
5. `College/src/*.py` → ❌ Separate college system

**Resolution:** Document `python -m app` as THE entry point, archive others

### **3. Configuration Fragmentation**
Multiple config systems coexist:
- Modern: `app/config/settings.py` + environment variables
- Legacy: JSON files in `config/` directory
- **Bridge:** `app/services/lights_service.py` imports `src.devices.smart_lights` ✅

**Note:** This bridge is **CORRECT** - proper layering where `app/` uses stable `src/` hardware

### **4. Import Path Dependencies**
- `app/services/lights_service.py` imports `from src.devices.smart_lights`
- This is **intentional** - app layer uses hardware abstraction
- Other `src/` scripts bypass the modern app entirely (problem)

---

## ✅ **Recent Fixes Applied (Oct 3, 2025)**

Per `FIXES_APPLIED.md`:

1. **WebSocket Connection Persistence**
   - Added periodic ping messages (every 30s)
   - Proper timeout handling with `asyncio.wait_for()`
   - Connection now stays alive reliably

2. **GameSnapshot Serialization**
   - Fixed `game_id` field aliasing to `"id"` for frontend
   - Added `by_alias=True` to model Config
   - Overrode `model_dump()` for consistent JSON output
   - DateTime objects now serialize properly

3. **WebSocket Manager Logging**
   - Added connection/disconnection tracking
   - Broadcast success/failure logging
   - Better visibility into real-time communication

4. **Frontend WebSocket Error Handling**
   - Comprehensive console logging
   - Connection lifecycle visibility
   - Message receipt confirmation

---

## 📋 **Database & Data**

### **Active Database**
- `data/history.db` - SQLite database for event history
- Schema appears functional but needs documentation

### **Configuration Files**
```
config/
├── celebrations.json                         # Active
├── stadium_config.json                       # Active
├── team_colors.json                          # Active (54 teams)
├── wiz_lights_config.json                    # Active (auto-generated)
├── team_colors_backup_20251003_184528.json   # Backup (delete after consolidation)
├── team_colors_backup_20251003_191003.json   # Backup (delete after consolidation)
└── team_colors_backup_comparison.json        # Backup (delete after consolidation)
```

### **Team Database Migration Ready**
- `migrate_team_database.py` script exists
- Will upgrade from 54 → 324 teams (5.9x increase)
- Adds logos, ESPN IDs, hex colors
- Creates backups before migration

---

## 🚀 **How to Start the System (Current)**

### **Backend**
```powershell
# Activate virtual environment (if using venv)
.venv\Scripts\Activate.ps1

# Start modern backend (port 8000)
python -m app
```

### **Frontend**
```powershell
# In separate terminal
cd dashboard
npm run dev
# Access at http://localhost:5173
```

### **Verification**
```powershell
# Test API
curl http://localhost:8000/api/status/

# Test WebSocket (see test_connection.py)
python test_connection.py
```

---

## 📦 **Dependencies**

### **Python (requirements.txt)**
- FastAPI 0.103.2
- uvicorn[standard] 0.23.2
- websockets 11.0.3
- pywizlight 0.5.14 (WiZ lights)
- requests, aiohttp, httpx (HTTP clients)
- pydantic 2.4.2 (data validation)
- pytest + pytest-asyncio (testing)

### **Node.js (dashboard/package.json)**
- React 19.1.1
- TypeScript 5.9.3
- Vite 7.1.7
- @tanstack/react-query 5.90.2
- dayjs 1.11.18

---

## 🧪 **Testing Status**

### **Backend Tests** (`tests/`)
- `test_status.py` - System health endpoint ✅
- `test_devices.py` - Device management ✅
- `test_games.py` - Game data API ✅
- `test_history.py` - Event history ✅
- `conftest.py` - Test fixtures with stubs ✅

**Run tests:**
```powershell
pytest tests/
```

### **Integration Tests**
- `test_connection.py` - WebSocket + API validation ✅

---

## 🎨 **Feature Completeness**

### **✅ Fully Implemented**
- [x] WiZ smart light control
- [x] 12 celebration types (touchdown, field goal, sack, etc.)
- [x] Team color database (54 teams, 324 ready to import)
- [x] Real-time WebSocket updates
- [x] FastAPI REST API with 6 route modules
- [x] React dashboard with live event feed
- [x] ESPN API integration
- [x] Red zone ambient lighting
- [x] Multi-game monitoring
- [x] Device management
- [x] Event history storage
- [x] Proper error handling & logging

### **⚠️ Partially Implemented**
- [ ] College football full integration (separate system exists)
- [ ] Multi-brand device support (WiZ only currently)
- [ ] User authentication (not needed for home use)
- [ ] Advanced celebration customization UI

### **📋 Not Implemented**
- [ ] Mobile app
- [ ] Sonos audio integration (placeholder)
- [ ] LED display integration (placeholder)
- [ ] Docker deployment
- [ ] Production deployment guides

---

## 🔍 **Known Issues**

### **Critical**
None - system is functional

### **High Priority**
1. **Legacy code confusion** - Multiple entry points
2. **College system separation** - Standalone vs integrated
3. **Team database needs migration** - Only 54/324 teams loaded

### **Medium Priority**
1. **Documentation outdated** - README describes old architecture
2. **No deployment automation** - Manual setup required
3. **Config backup clutter** - Multiple backup JSON files

### **Low Priority**
1. **Test coverage incomplete** - No E2E tests for full flow
2. **No CI/CD pipeline** - Manual testing only
3. **Environment variable docs missing** - No .env.example

---

## 📝 **Immediate Next Steps (Recommended)**

1. **Create this documentation** ✅ (you are here)
2. **Commit current state to git** → Safety checkpoint
3. **Archive legacy code** → Clean structure
4. **Run team database migration** → Full team roster
5. **Update README** → Reflect modern architecture
6. **Test consolidated system** → Verify no regressions

---

## 🎯 **Success Criteria for Consolidation**

### **Phase 1: Archive Legacy (Safe & Reversible)**
- [ ] Move `api/` → `archive/api-legacy/`
- [ ] Move legacy CLI scripts → `archive/src-cli/`
- [ ] Keep `src/devices/` and `src/sports/` (used by app)
- [ ] Document single entry point: `python -m app`
- [ ] Git commit with clear message

### **Phase 2: College Integration (Optional)**
- [ ] Decide: merge College/ into app/ OR keep standalone
- [ ] If merge: migrate monitoring logic to `app/services/`
- [ ] Unified dashboard shows NFL + College

### **Phase 3: Data Cleanup**
- [ ] Run `migrate_team_database.py`
- [ ] Delete backup JSON files
- [ ] Document active config files
- [ ] Create `.env.example`

### **Phase 4: Documentation**
- [ ] Update main README
- [ ] Create QUICKSTART.md
- [ ] Document environment variables
- [ ] Add troubleshooting guide

---

## 🔗 **Related Documentation**

- `INTEGRATION_REPORT.md` - Team database migration plan
- `FIXES_APPLIED.md` - Recent WebSocket & serialization fixes
- `README.md` - Main project documentation (needs update)
- `dashboard/README.md` - Frontend documentation
- `College/README.md` - College football system docs

---

## 💡 **Technical Debt Summary**

| Category | Severity | Effort | Impact |
|----------|----------|--------|--------|
| Dual backend architectures | High | Low | High |
| Multiple entry points | Medium | Low | High |
| Legacy CLI scripts | Low | Low | Medium |
| Documentation outdated | Medium | Medium | High |
| No deployment automation | Low | High | Medium |
| College system separation | Medium | High | High |
| Test coverage gaps | Low | High | Low |

**Total Technical Debt:** ~3-4 days of focused work to fully resolve

---

## ✅ **What's Working Well**

1. **Modern backend is solid** - Proper DI, clean API, good patterns
2. **Frontend is polished** - React + TS, WebSocket integration working
3. **Hardware control is stable** - WiZ lights working reliably
4. **Recent fixes successful** - WebSocket persistence solved
5. **Test infrastructure exists** - Fixtures and stubs in place
6. **Configuration flexible** - JSON + environment variables
7. **Team colors comprehensive** - 324 teams ready to import

---

## 🚨 **Warnings & Gotchas**

1. **Don't delete `src/devices/`** - Still used by `app/services/`
2. **Don't delete `src/sports/`** - Sport monitors still used
3. **Config JSONs are active** - Don't delete main config files
4. **Virtual environment required** - System won't run without dependencies
5. **Port 8000 must be free** - Backend won't start if occupied
6. **Node.js required for dashboard** - Frontend won't build without it

---

## 📞 **Support & Contacts**

- **Repository:** github.com/mdhenninger/smart-stadium
- **Branch:** main
- **Python Version:** 3.8+
- **Node Version:** 16+

---

*This document created as pre-consolidation checkpoint on October 4, 2025*
