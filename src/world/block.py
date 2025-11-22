"""
src/world/block.py
Block/Tile class for environment
"""
import pygame
from src.config.settings import *

class Block:
    def __init__(self, x, y, block_type, asset_manager, destructible=True):
        self.grid_x = x
        self.grid_y = y
        self.block_type = block_type
        self.destructible = destructible
        self.asset_manager = asset_manager
        
        # Create rect for collision
        self.rect = pygame.Rect(
            x * TILE_SIZE,
            y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )
    
    def render(self, screen, camera_x, camera_y):
        """Render block"""
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Get sprite or use placeholder
        sprite = self.asset_manager.get_sprite(f'block_{self.block_type}')
        if sprite:
            screen.blit(sprite, (screen_x, screen_y))
        else:
            # Enhanced block rendering with depth
            if self.block_type == 'stone':
                base_color = (120, 120, 120)
                dark_color = (80, 80, 80)
                light_color = (160, 160, 160)
            else:  # dirt
                base_color = (139, 69, 19)
                dark_color = (101, 50, 14)
                light_color = (160, 82, 45)
            
            # Main block
            block_rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, base_color, block_rect)
            
            # Top highlight (light)
            pygame.draw.line(screen, light_color, (screen_x, screen_y), (screen_x + TILE_SIZE - 1, screen_y), 2)
            pygame.draw.line(screen, light_color, (screen_x, screen_y), (screen_x, screen_y + TILE_SIZE - 1), 2)
            
            # Bottom shadow (dark)
            pygame.draw.line(screen, dark_color, (screen_x + TILE_SIZE - 1, screen_y), 
                           (screen_x + TILE_SIZE - 1, screen_y + TILE_SIZE - 1), 2)
            pygame.draw.line(screen, dark_color, (screen_x, screen_y + TILE_SIZE - 1), 
                           (screen_x + TILE_SIZE - 1, screen_y + TILE_SIZE - 1), 2)
            
            # Border
            pygame.draw.rect(screen, (40, 40, 40), block_rect, 1)