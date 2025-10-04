# Govee Integration Archive

This directory contains the archived Govee H6009 cloud API integration that was removed from the Smart Stadium system.

## Why Removed

The Govee cloud API has aggressive rate limiting (1 request per second) that made it incompatible with the fast-paced celebration sequences required for live sports monitoring. Issues encountered:

- **Rate limiting**: Free tier limited to 1 request/second
- **Cloud latency**: 200-500ms response times vs WiZ local UDP ~50ms
- **Synchronization issues**: Could not keep up with WiZ lights during multi-flash celebrations
- **Auto-reset failures**: API would drop commands when trying to return to default lighting after celebrations
- **Slowdown impact**: Had to slow ALL lights from 0.5s/flash → 1.0s/flash to accommodate Govee

## Archived Files

- `govee_lights.py` - GoveeLightController and GoveeStadiumLights classes
- `govee_config.json` - Device configuration (API key: f1454325-8c4e-456a-9f36-1954a45c762c)
- `query_govee_api.py` - API discovery utility
- `GOVEE_INTEGRATION.md` - Full integration documentation

## Device Information

- **Model**: Govee H6009 RGBWW Bulb
- **Device ID**: F3:1C:D0:C9:07:DE:C6:14
- **Location**: Zone 4 (Stadium Light 4)
- **API**: https://developer-api.govee.com/v1/devices

## Restoration

If you want to restore the Govee integration:

1. Move files back from archive to their original locations
2. Set `"enabled": true` in `govee_config.json`
3. Restore Govee controller initialization in `app/services/lights_service.py`
4. Accept that celebrations will be slower (1.0s per flash) to accommodate API limits
5. Manually trigger "Default Lighting" after celebrations (auto-reset doesn't work reliably)

## Alternative: Local Control

Consider investigating Govee LAN API if available for your device model. This would require:
- Enabling "LAN Control" in Govee Home app
- Using local UDP/TCP instead of cloud HTTPS
- Much lower latency and no rate limits
- Model H6009 may not support LAN control (check Govee documentation)

---

**Archived**: October 4, 2025
**Reason**: Cloud API rate limiting incompatible with real-time sports celebrations
