"""
Smart Stadium API - Devices Router
Endpoints for device management and control
"""

from typing import List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends

from models import (
    ApiResponse, Device, DeviceToggleRequest, DeviceAddRequest, 
    LightingRequest, DeviceStatus, DeviceType
)

router = APIRouter()

def get_stadium_api():
    """Dependency to get the stadium API instance"""
    from main import stadium_api
    if not stadium_api.device_manager:
        raise HTTPException(status_code=503, detail="Device manager not initialized")
    return stadium_api

@router.get("/", response_model=ApiResponse)
async def get_devices(stadium_api = Depends(get_stadium_api)):
    """Get all managed devices with their status"""
    try:
        devices = []
        device_status = await stadium_api.device_manager.get_device_status_summary()
        
        for device_id, device_info in stadium_api.device_manager.managed_devices.items():
            # Check if device is online
            status = DeviceStatus.ONLINE if device_info.get('last_seen', 0) > (datetime.now().timestamp() - 30) else DeviceStatus.OFFLINE
            
            devices.append(Device(
                id=device_id,
                name=device_info.get('name', f"Device {device_id}"),
                ip_address=device_info.get('ip', 'Unknown'),
                device_type=DeviceType.WIZ,  # Default to WiZ for now
                status=status,
                enabled=device_info.get('enabled', False),
                last_seen=datetime.fromtimestamp(device_info.get('last_seen', 0)).isoformat() if device_info.get('last_seen') else None,
                response_time_ms=device_info.get('response_time', None)
            ))
        
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(devices)} devices",
            data={
                "devices": [device.model_dump() for device in devices],
                "summary": device_status
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get devices: {str(e)}")

@router.get("/{device_id}", response_model=ApiResponse)
async def get_device(device_id: str, stadium_api = Depends(get_stadium_api)):
    """Get specific device information"""
    try:
        if device_id not in stadium_api.device_manager.managed_devices:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        device_info = stadium_api.device_manager.managed_devices[device_id]
        status = DeviceStatus.ONLINE if device_info.get('last_seen', 0) > (datetime.now().timestamp() - 30) else DeviceStatus.OFFLINE
        
        device = Device(
            id=device_id,
            name=device_info.get('name', f"Device {device_id}"),
            ip_address=device_info.get('ip', 'Unknown'),
            device_type=DeviceType.WIZ,
            status=status,
            enabled=device_info.get('enabled', False),
            last_seen=datetime.fromtimestamp(device_info.get('last_seen', 0)).isoformat() if device_info.get('last_seen') else None,
            response_time_ms=device_info.get('response_time', None)
        )
        
        return ApiResponse(
            success=True,
            message=f"Device {device_id} information",
            data=device.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get device: {str(e)}")

@router.put("/{device_id}/toggle", response_model=ApiResponse)
async def toggle_device(device_id: str, request: DeviceToggleRequest, stadium_api = Depends(get_stadium_api)):
    """Enable or disable a device"""
    try:
        if device_id not in stadium_api.device_manager.managed_devices:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        # Update device enabled status
        stadium_api.device_manager.managed_devices[device_id]['enabled'] = request.enabled
        
        # Save configuration
        await stadium_api.device_manager.save_device_config()
        
        # Update enabled devices list
        stadium_api.device_manager.enabled_devices = [
            device_id for device_id, info in stadium_api.device_manager.managed_devices.items()
            if info.get('enabled', False)
        ]
        
        action = "enabled" if request.enabled else "disabled"
        device_name = stadium_api.device_manager.managed_devices[device_id].get('name', device_id)
        
        return ApiResponse(
            success=True,
            message=f"Device {device_name} {action}",
            data={"device_id": device_id, "enabled": request.enabled}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle device: {str(e)}")

@router.post("/add", response_model=ApiResponse)
async def add_device(request: DeviceAddRequest, stadium_api = Depends(get_stadium_api)):
    """Add a new device to the system"""
    try:
        # Generate device ID
        device_id = f"{request.device_type.value}_{request.ip_address.replace('.', '_')}"
        
        # Check if device already exists
        if device_id in stadium_api.device_manager.managed_devices:
            raise HTTPException(status_code=400, detail=f"Device with IP {request.ip_address} already exists")
        
        # Add device to managed devices
        stadium_api.device_manager.managed_devices[device_id] = {
            'name': request.name,
            'ip': request.ip_address,
            'enabled': request.enabled,
            'device_type': request.device_type.value,
            'added_timestamp': datetime.now().timestamp()
        }
        
        # Save configuration
        await stadium_api.device_manager.save_device_config()
        
        # Update enabled devices list if device is enabled
        if request.enabled:
            stadium_api.device_manager.enabled_devices.append(device_id)
        
        return ApiResponse(
            success=True,
            message=f"Device {request.name} added successfully",
            data={"device_id": device_id, "name": request.name, "ip": request.ip_address}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add device: {str(e)}")

@router.delete("/{device_id}", response_model=ApiResponse)
async def remove_device(device_id: str, stadium_api = Depends(get_stadium_api)):
    """Remove a device from the system"""
    try:
        if device_id not in stadium_api.device_manager.managed_devices:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        device_name = stadium_api.device_manager.managed_devices[device_id].get('name', device_id)
        
        # Remove from managed devices
        del stadium_api.device_manager.managed_devices[device_id]
        
        # Remove from enabled devices if present
        if device_id in stadium_api.device_manager.enabled_devices:
            stadium_api.device_manager.enabled_devices.remove(device_id)
        
        # Save configuration
        await stadium_api.device_manager.save_device_config()
        
        return ApiResponse(
            success=True,
            message=f"Device {device_name} removed successfully",
            data={"device_id": device_id, "removed": True}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove device: {str(e)}")

@router.post("/{device_id}/test", response_model=ApiResponse)
async def test_device(device_id: str, stadium_api = Depends(get_stadium_api)):
    """Test connectivity to a specific device"""
    try:
        if device_id not in stadium_api.device_manager.managed_devices:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        device_info = stadium_api.device_manager.managed_devices[device_id]
        device_ip = device_info.get('ip')
        
        if not device_ip:
            raise HTTPException(status_code=400, detail="Device IP not found")
        
        # Test device connectivity
        is_online = await stadium_api.device_manager.check_device_status(device_ip)
        
        return ApiResponse(
            success=True,
            message=f"Device test completed",
            data={
                "device_id": device_id,
                "ip_address": device_ip,
                "status": "online" if is_online else "offline",
                "test_timestamp": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Device test failed: {str(e)}")

@router.post("/lighting/default", response_model=ApiResponse)
async def set_default_lighting(stadium_api = Depends(get_stadium_api)):
    """Set all enabled devices to default warm white lighting"""
    try:
        if not stadium_api.stadium_lights:
            raise HTTPException(status_code=503, detail="Stadium lights not initialized")
        
        await stadium_api.stadium_lights.set_all_default_lighting()
        
        return ApiResponse(
            success=True,
            message="All devices set to default lighting (2700K warm white)",
            data={"lighting_mode": "default", "color_temp": 2700, "brightness": 180}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set default lighting: {str(e)}")

@router.post("/lighting/custom", response_model=ApiResponse)
async def set_custom_lighting(request: LightingRequest, stadium_api = Depends(get_stadium_api)):
    """Set custom lighting for all enabled devices"""
    try:
        if not stadium_api.stadium_lights:
            raise HTTPException(status_code=503, detail="Stadium lights not initialized")
        
        if request.color_rgb:
            # Set specific RGB color
            r, g, b = request.color_rgb
            brightness = request.brightness or 255
            await stadium_api.stadium_lights.flash_all_color((r, g, b), duration=0)  # Permanent color
            
            return ApiResponse(
                success=True,
                message=f"All devices set to RGB({r}, {g}, {b}) at brightness {brightness}",
                data={"color_rgb": request.color_rgb, "brightness": brightness}
            )
            
        elif request.color_temp:
            # Set color temperature
            color_temp = request.color_temp
            brightness = request.brightness or 180
            
            # This would require implementing color temperature setting in the stadium lights
            # For now, fall back to default lighting
            await stadium_api.stadium_lights.set_all_default_lighting()
            
            return ApiResponse(
                success=True,
                message=f"Color temperature lighting requested (falling back to default)",
                data={"color_temp": color_temp, "brightness": brightness}
            )
            
        else:
            raise HTTPException(status_code=400, detail="Either color_rgb or color_temp must be specified")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set custom lighting: {str(e)}")

@router.post("/refresh", response_model=ApiResponse)
async def refresh_device_status(stadium_api = Depends(get_stadium_api)):
    """Refresh the status of all managed devices"""
    try:
        # Trigger device status refresh
        device_status = await stadium_api.device_manager.get_device_status_summary()
        
        return ApiResponse(
            success=True,
            message="Device status refreshed",
            data={
                "refresh_timestamp": datetime.now().isoformat(),
                "device_summary": device_status
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh device status: {str(e)}")