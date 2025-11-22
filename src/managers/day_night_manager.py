"""
src/managers/day_night_manager.py
Day/night cycle management
"""
from src.config.settings import *

class DayNightManager:
    def __init__(self):
        self.time = 0  # Time in seconds
        self.cycle_duration = DAY_NIGHT_CYCLE_DURATION
        self.day_count = 0
        self.last_day = 0
    
    def update(self, dt):
        """Update time"""
        self.time += dt
        
        # Check if day changed
        current_day = int(self.time / self.cycle_duration)
        if current_day > self.last_day:
            self.day_count += 1
            self.last_day = current_day
    
    def get_time_of_day(self):
        """Get current time in cycle (0.0 to 1.0)"""
        return (self.time % self.cycle_duration) / self.cycle_duration
    
    def is_day(self):
        """Check if it's daytime"""
        time_of_day = self.get_time_of_day()
        return 0.25 < time_of_day < 0.75
    
    def is_night(self):
        """Check if it's nighttime"""
        return not self.is_day()
    
    def get_overlay_alpha(self):
        """Get darkness overlay alpha (0-150)"""
        time_of_day = self.get_time_of_day()
        
        if time_of_day < 0.25:  # Night to dawn
            return int(150 * (1 - time_of_day / 0.25))
        elif time_of_day < 0.5:  # Day
            return 0
        elif time_of_day < 0.75:  # Dusk
            return int(150 * ((time_of_day - 0.5) / 0.25))
        else:  # Night
            return 150
    
    def should_reset_map(self):
        """Check if exploration map should reset"""
        return self.day_count > 0 and self.day_count % EXPLORATION_RESET_DAYS == 0
    
    def get_day_count(self):
        """Get current day"""
        return self.day_count