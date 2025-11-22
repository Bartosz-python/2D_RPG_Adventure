"""
src/managers/state_manager.py
Game state management
"""

class StateManager:
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.previous_state = None
    
    def set_state(self, new_state):
        """Change game state"""
        self.previous_state = self.current_state
        self.current_state = new_state
    
    def get_state(self):
        """Get current state"""
        return self.current_state
    
    def get_previous_state(self):
        """Get previous state"""
        return self.previous_state