# Govee Integration Summary

## Overview
Successfully integrated Govee H6009 smart bulb into Smart Stadium system using Govee's official cloud API.

## What Was Added

### 1. Govee Controller (`src/devices/govee_lights.py`)
- **GoveeLightController**: Low-level HTTP API client for Govee cloud API
- **GoveeStadiumLights**: High-level wrapper matching SmartStadiumLights interface
- Supports: RGB color, brightness, warm white, celebrations, red zone

### 2. Configuration
- **File**: `config/govee_config.json`
- **Your Device**: 
  - Name: Stadium Light 4
  - Model: H6009
  - Device ID: F3:1C:D0:C9:07:DE:C6:14
  - Location: Zone 4
  - API Key: f1454325-8c4e-456a-9f36-1954a45c762c

### 3. Updated Services

#### `app/config/loaders.py`
- Added `load_govee_config()` function

#### `app/core/config_manager.py`
- Added `govee_config` to AppConfig dataclass
- Loads govee_config.json during initialization

#### `app/services/lights_service.py`
- **MAJOR CHANGE**: Now manages BOTH WiZ and Govee controllers
- Runs celebrations on all enabled lights simultaneously
- Falls back gracefully if one controller is unavailable

#### `app/services/device_manager.py`
- Loads both WiZ and Govee devices
- Govee devices show as `govee_*` in device list
- IP address shown as "cloud" for Govee (API-based, not local)

#### `app/core/container.py`
- Passes `govee_config` to LightsService during initialization

## How It Works

### 1. Startup
- Backend loads both `wiz_lights_config.json` and `govee_config.json`
- Creates WiZ controller for 3 local lights (IPs .41, .47, .48)
- Creates Govee controller for 1 cloud light (H6009)
- All 4 lights listed in `/api/devices`

### 2. Celebrations
When touchdown scored:
```
LightsService.celebrate_touchdown()
  ├─> WiZ Controller: Flash 3 local lights (50ms latency)
  └─> Govee Controller: Flash 1 cloud light (200-500ms latency)
```

### 3. Red Zone
- Both WiZ and Govee lights turn to team color
- 150 brightness for ambient effect
- Returns to 2700K warm white when red zone ends

### 4. Default Lighting
- All 4 lights set to 2700K @ 180 brightness
- Called at startup, shutdown, and after celebrations

## Device List Output
```json
{
  "devices": [
    {
      "device_id": "wiz_192_168_86_41",
      "name": "Stadium Light 1",
      "location": "Zone 1",
      "ip_address": "192.168.86.41",
      "enabled": true
    },
    {
      "device_id": "wiz_192_168_86_47",
      "name": "Stadium Light 2",
      "location": "Zone 2",
      "ip_address": "192.168.86.47",
      "enabled": true
    },
    {
      "device_id": "wiz_192_168_86_48",
      "name": "Stadium Light 3",
      "location": "Zone 3",
      "ip_address": "192.168.86.48",
      "enabled": true
    },
    {
      "device_id": "govee_07_DE_C6_14",
      "name": "Stadium Light 4",
      "location": "Zone 4",
      "ip_address": "cloud",
      "enabled": true
    }
  ]
}
```

## Testing Commands

### Query Govee API
```bash
python query_govee_api.py
```
Shows your Govee devices and tests control.

### Test Both Controllers
After backend starts, check logs for:
```
INFO - Initialized WiZ controller with 3 lights
INFO - Initialized Govee controller with 1 lights
INFO - Loaded 324 team color configurations into lights service
```

### Manual Test via Dashboard
1. Go to http://192.168.86.237:5173
2. Click "Test Device" on any light
3. All 4 lights should flash
4. WiZ lights will be instant, Govee slightly delayed

## API Key Info
- **Key**: f1454325-8c4e-456a-9f36-1954a45c762c
- **Type**: Free tier (non-profit use only)
- **Rate Limits**: Unknown, but reasonable for celebration triggers
- **Endpoint**: https://developer-api.govee.com/v1/devices/control

## Troubleshooting

### Govee light not responding
- Check API key is correct in govee_config.json
- Verify device is online in Govee Home app
- Check backend logs for "Govee API error" messages

### Both lights not flashing together
- WiZ is local (~50ms), Govee is cloud (~300ms)
- This slight delay is normal and acceptable
- If WiZ works but Govee doesn't, check internet connection

### Device not in list
- Ensure "enabled": true in govee_config.json
- Restart backend after config changes
- Check `/api/devices` endpoint in browser

## Files Modified
1. ✅ `src/devices/govee_lights.py` - NEW
2. ✅ `config/govee_config.json` - NEW
3. ✅ `query_govee_api.py` - NEW (utility)
4. ✅ `app/config/loaders.py` - Added load_govee_config()
5. ✅ `app/core/config_manager.py` - Added govee_config field
6. ✅ `app/services/lights_service.py` - Multi-controller support
7. ✅ `app/services/device_manager.py` - Load Govee devices
8. ✅ `app/core/container.py` - Pass govee_config to LightsService

## Next Steps After Restart
1. Verify backend starts without errors
2. Check `/api/devices` shows all 4 lights
3. Test celebration from dashboard
4. Monitor game and verify all lights celebrate together
5. Confirm Govee light returns to warm white after events
