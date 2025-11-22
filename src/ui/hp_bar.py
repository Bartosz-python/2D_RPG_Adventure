"""
src/ui/hp_bar.py
Health bar component
"""
import pygame
from src.config.settings import *

class HPBar:
    def __init__(self, x, y, width=200, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 24)
    
    def render(self, screen, current_hp, max_hp):
        """Render HP bar"""
        # Background
        pygame.draw.rect(screen, HP_BAR_BG, (self.x, self.y, self.width, self.height))
        
        # HP
        hp_percentage = current_hp / max_hp if max_hp > 0 else 0
        hp_width = int(self.width * hp_percentage)
        pygame.draw.rect(screen, HP_BAR_COLOR, (self.x, self.y, hp_width, self.height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
        
        # Text
        hp_text = self.font.render(f"HP: {current_hp}/{max_hp}", True, WHITE)
        screen.blit(hp_text, (self.x + 5, self.y + 2))