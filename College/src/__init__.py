"""
College Football Smart Light Celebration System
Multi-game monitoring with team selection and custom colors
"""

from .college_celebrations import CollegeCelebrationController, COLLEGE_TEAM_COLORS
from .college_game_monitor import CollegeGameMonitor

__version__ = "1.0.0"
__author__ = "College Football Fan"
__description__ = "Smart light system for celebrating any college football team with multi-game monitoring"

__all__ = ['CollegeCelebrationController', 'CollegeGameMonitor', 'COLLEGE_TEAM_COLORS']