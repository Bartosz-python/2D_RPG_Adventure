"""
src/managers/quest_manager.py
Quest system management
"""
from src.config.settings import *

class QuestManager:
    def __init__(self):
        self.current_quest = None
        self.completed_quests = []
        self.tutorial_complete = False
        self.tutorial_stage = 0
    
    def start_tutorial(self):
        """Start tutorial quest"""
        self.current_quest = {
            'name': 'Tutorial',
            'description': 'Learn the basics',
            'objectives': [
                'Move around',
                'Jump',
                'Interact with object',
                'Destroy block',
                'Fight enemy'
            ],
            'completed_objectives': [False] * 5
        }
        self.tutorial_stage = 0
    
    def update_tutorial(self, player, dt):
        """Update tutorial progress"""
        if not self.current_quest:
            self.start_tutorial()
            return False
        
        objectives = self.current_quest['completed_objectives']
        
        # Check tutorial objectives
        if not objectives[0] and (player.keys['left'] or player.keys['right']):
            objectives[0] = True
            self.tutorial_stage = 1
        
        if not objectives[1] and player.keys['jump']:
            objectives[1] = True
            self.tutorial_stage = 2
        
        # Additional objectives would be checked based on game events
        
        # Check if tutorial is complete
        if all(objectives):
            self.tutorial_complete = True
            self.completed_quests.append(self.current_quest)
            self.current_quest = None
            return True
        
        return False
    
    def handle_tutorial_input(self, event, player):
        """Handle tutorial-specific input"""
        import pygame
        if event.key == pygame.K_RETURN:
            if not self.current_quest:
                self.start_tutorial()
    
    def get_active_quest(self):
        """Get currently active quest"""
        return self.current_quest
    
    def is_tutorial_complete(self):
        """Check if tutorial is done"""
        return self.tutorial_complete