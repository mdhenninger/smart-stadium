"""
Smart Stadium Configuration Manager

Handles loading and managing configuration for:
- Device settings (lights, audio, displays)
- Sport preferences and team selections
- Celebration customizations
- System settings
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """Manages Smart Stadium configuration files and settings"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration manager"""
        self.logger = logging.getLogger(__name__)
        
        # Set config directory (default to ../config from src)
        if config_dir is None:
            self.config_dir = Path(__file__).parent.parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)
            
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration file paths
        self.stadium_config_path = self.config_dir / "stadium_config.json"
        self.team_colors_path = self.config_dir / "team_colors.json"
        self.celebrations_path = self.config_dir / "celebrations.json"
        
        self.logger.info(f"Config directory: {self.config_dir}")
    
    async def load_config(self) -> Dict[str, Any]:
        """Load complete Smart Stadium configuration"""
        config = {
            'stadium': await self._load_stadium_config(),
            'team_colors': await self._load_team_colors(),
            'celebrations': await self._load_celebrations(),
            'devices': {},
            'sports': {}
        }
        
        # Extract device and sport configs from stadium config
        stadium_config = config['stadium']
        config['devices'] = stadium_config.get('devices', {})
        config['sports'] = stadium_config.get('sports', {})
        
        self.logger.info("✅ Configuration loaded successfully")
        return config
    
    async def _load_stadium_config(self) -> Dict[str, Any]:
        """Load main stadium configuration"""
        if not self.stadium_config_path.exists():
            # Create default config if none exists
            default_config = self._create_default_stadium_config()
            await self._save_json(self.stadium_config_path, default_config)
            self.logger.info("📝 Created default stadium configuration")
            return default_config
        
        return await self._load_json(self.stadium_config_path)
    
    async def _load_team_colors(self) -> Dict[str, Any]:
        """Load team color definitions"""
        if not self.team_colors_path.exists():
            # Create default team colors
            default_colors = self._create_default_team_colors()
            await self._save_json(self.team_colors_path, default_colors)
            self.logger.info("🎨 Created default team colors")
            return default_colors
        
        return await self._load_json(self.team_colors_path)
    
    async def _load_celebrations(self) -> Dict[str, Any]:
        """Load celebration definitions"""
        if not self.celebrations_path.exists():
            # Create default celebrations
            default_celebrations = self._create_default_celebrations()
            await self._save_json(self.celebrations_path, default_celebrations)
            self.logger.info("🎉 Created default celebrations")
            return default_celebrations
        
        return await self._load_json(self.celebrations_path)
    
    async def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file safely"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            return {}
    
    async def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Save JSON file safely"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving {file_path}: {e}")
    
    def _create_default_stadium_config(self) -> Dict[str, Any]:
        """Create default stadium configuration"""
        return {
            "stadium_name": "My Smart Stadium",
            "devices": {
                "smart_lights": {
                    "type": "wiz",
                    "ips": [
                        "192.168.86.41",
                        "192.168.86.47", 
                        "192.168.86.48"
                    ],
                    "enabled": True
                },
                "audio_system": {
                    "type": "sonos",
                    "enabled": False,
                    "volume": 0.7
                },
                "displays": {
                    "enabled": False
                }
            },
            "sports": {
                "nfl": {
                    "enabled": True,
                    "polling_interval": 10,
                    "favorite_teams": ["BUF"]
                },
                "college": {
                    "enabled": True,
                    "polling_interval": 15,
                    "favorite_teams": []
                },
                "nba": {
                    "enabled": False
                }
            },
            "celebrations": {
                "touchdown_duration": 10,
                "red_zone_style": "solid",
                "victory_duration": 30
            }
        }
    
    def _create_default_team_colors(self) -> Dict[str, Any]:
        """Create default NFL team colors (from our existing system)"""
        return {
            "nfl": {
                "BUF": {"primary": [0, 51, 141], "secondary": [198, 12, 48]},
                "MIA": {"primary": [0, 142, 204], "secondary": [252, 76, 2]},
                "NE": {"primary": [0, 34, 68], "secondary": [198, 12, 48]},
                "NYJ": {"primary": [18, 87, 64], "secondary": [255, 255, 255]},
                "BAL": {"primary": [26, 25, 95], "secondary": [158, 124, 12]},
                "CIN": {"primary": [251, 79, 20], "secondary": [0, 0, 0]},
                "CLE": {"primary": [49, 29, 0], "secondary": [255, 60, 0]},
                "PIT": {"primary": [255, 182, 18], "secondary": [0, 0, 0]},
                "HOU": {"primary": [3, 32, 47], "secondary": [167, 25, 48]},
                "IND": {"primary": [0, 44, 95], "secondary": [255, 255, 255]},
                "JAX": {"primary": [0, 103, 120], "secondary": [215, 162, 42]},
                "TEN": {"primary": [12, 35, 64], "secondary": [75, 146, 219]},
                "DEN": {"primary": [251, 79, 20], "secondary": [0, 34, 68]},
                "KC": {"primary": [227, 24, 55], "secondary": [255, 184, 28]},
                "LV": {"primary": [165, 172, 175], "secondary": [0, 0, 0]},
                "LAC": {"primary": [0, 128, 198], "secondary": [255, 194, 14]},
                "DAL": {"primary": [0, 34, 68], "secondary": [134, 147, 151]},
                "NYG": {"primary": [1, 35, 82], "secondary": [163, 13, 45]},
                "PHI": {"primary": [0, 76, 84], "secondary": [165, 172, 175]},
                "WAS": {"primary": [90, 20, 20], "secondary": [255, 182, 18]},
                "CHI": {"primary": [11, 22, 42], "secondary": [200, 56, 3]},
                "DET": {"primary": [0, 118, 182], "secondary": [165, 172, 175]},
                "GB": {"primary": [24, 48, 40], "secondary": [255, 184, 28]},
                "MIN": {"primary": [79, 38, 131], "secondary": [255, 198, 47]},
                "ATL": {"primary": [167, 25, 48], "secondary": [0, 0, 0]},
                "CAR": {"primary": [0, 133, 202], "secondary": [165, 172, 175]},
                "NO": {"primary": [211, 188, 141], "secondary": [0, 0, 0]},
                "TB": {"primary": [213, 10, 10], "secondary": [52, 48, 43]},
                "ARI": {"primary": [151, 35, 63], "secondary": [255, 255, 255]},
                "LAR": {"primary": [0, 53, 148], "secondary": [255, 209, 0]},
                "SF": {"primary": [170, 0, 0], "secondary": [173, 153, 93]},
                "SEA": {"primary": [0, 34, 68], "secondary": [105, 190, 40]}
            }
        }
    
    def _create_default_celebrations(self) -> Dict[str, Any]:
        """Create default celebration definitions"""
        return {
            "touchdown": {
                "duration": 10,
                "pattern": "pulse_team_colors",
                "intensity": "high"
            },
            "field_goal": {
                "duration": 5,
                "pattern": "flash_team_colors", 
                "intensity": "medium"
            },
            "red_zone": {
                "style": "solid_team_color",
                "brightness": 150
            },
            "victory": {
                "duration": 30,
                "pattern": "celebration_wave",
                "intensity": "maximum"
            },
            "turnover": {
                "duration": 8,
                "pattern": "strobe_team_colors",
                "intensity": "high"
            }
        }