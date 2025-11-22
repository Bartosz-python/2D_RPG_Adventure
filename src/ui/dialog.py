"""
src/ui/dialog.py
Dialog box component
"""
import pygame
from src.config.settings import *

class Dialog:
    def __init__(self, text, asset_manager):
        self.text = text
        self.asset_manager = asset_manager
        self.font = pygame.font.Font(None, 28)
        self.width = 600
        self.height = 150
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 50
        self.visible = True
    
    def render(self, screen):
        """Render dialog box"""
        if not self.visible:
            return
        
        # Box
        pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 3)
        
        # Text (wrapped)
        words = self.text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font.size(test_line)[0] < self.width - 40:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Render lines
        y_offset = self.y + 20
        for line in lines:
            text_surface = self.font.render(line, True, WHITE)
            screen.blit(text_surface, (self.x + 20, y_offset))
            y_offset += 35
        
        # Continue prompt
        prompt = self.font.render("Press SPACE to continue", True, LIGHT_GRAY)
        screen.blit(prompt, (self.x + self.width - 250, self.y + self.height - 35))
    
    def close(self):
        """Close dialog"""
        self.visible = False