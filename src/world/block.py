"""
src/world/block.py
Block/Tile class for environment
"""
import pygame
from src.config.settings import *

class Block:
    def __init__(self, x, y, block_type, asset_manager, destructible=True, is_platform=False):
        self.grid_x = x
        self.grid_y = y
        self.block_type = block_type
        self.destructible = destructible
        self.asset_manager = asset_manager
        self.is_platform = is_platform  # One-way platform flag
        
        # Block HP system
        BLOCK_DURABILITY = {
            'dirt': 10,
            'stone': 50,
            'copper': 75,
            'copper_ore': 75  # Alias for compatibility
        }
        self.max_hp = BLOCK_DURABILITY.get(block_type, 10) if destructible else float('inf')
        self.hp = self.max_hp
        
        # Platforms are always TILE_SIZE wide and thin (4 pixels thick)
        if is_platform:
            PLATFORM_WIDTH = TILE_SIZE * 2  # Same width as destroyable blocks
            PLATFORM_HEIGHT = 4  # Thin platform
            BLOCK_SIZE = PLATFORM_WIDTH
            self.block_size = BLOCK_SIZE
            # Create rect for collision (aligned to top line of block)
            self.rect = pygame.Rect(
                x * TILE_SIZE,
                y * TILE_SIZE,
                PLATFORM_WIDTH,
                PLATFORM_HEIGHT
            )
        else:
            # Destroyable blocks are 2x2 size (extending to bottom-right)
            # Non-destructible blocks remain 1x1
            if destructible:
                BLOCK_SIZE = TILE_SIZE * 2
            else:
                BLOCK_SIZE = TILE_SIZE
            
            # Create rect for collision
            self.rect = pygame.Rect(
                x * TILE_SIZE,
                y * TILE_SIZE,
                BLOCK_SIZE,
                BLOCK_SIZE
            )
            self.block_size = BLOCK_SIZE  # Store for rendering
    
    def take_damage(self, damage):
        """Apply damage to block, returns True if block is destroyed"""
        if not self.destructible:
            return False
        self.hp -= damage
        if self.hp <= 0:
            return True
        return False
    
    def render(self, screen, camera_x, camera_y):
        """Render block"""
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Render platform differently
        if self.is_platform:
            # Draw platform as a thin horizontal line
            platform_color = (100, 150, 200)  # Light blue color for platforms
            platform_rect = pygame.Rect(screen_x, screen_y, self.rect.width, self.rect.height)
            pygame.draw.rect(screen, platform_color, platform_rect)
            # Add a subtle highlight on top
            pygame.draw.line(screen, (150, 200, 255), (screen_x, screen_y), 
                           (screen_x + self.rect.width, screen_y), 1)
            return
        
        # Use stored block size
        BLOCK_SIZE = self.block_size
        
        # Get sprite or use placeholder
        sprite = self.asset_manager.get_sprite(f'block_{self.block_type}')
        if sprite:
            # Scale sprite to block size if needed
            if sprite.get_size() != (BLOCK_SIZE, BLOCK_SIZE):
                sprite = pygame.transform.scale(sprite, (BLOCK_SIZE, BLOCK_SIZE))
            screen.blit(sprite, (screen_x, screen_y))
        else:
            # Enhanced block rendering with depth
            if self.block_type == 'stone':
                # Check if this is a bottom barrier block (non-destructible at very bottom)
                # Bottom barrier blocks are at y >= 170 (approximately bottom 4 screen lengths)
                # Use very dark color for bottom barrier blocks
                if not self.destructible and self.grid_y >= 170:
                    base_color = (20, 20, 20)  # Very dark
                    dark_color = (10, 10, 10)  # Almost black
                    light_color = (30, 30, 30)  # Slightly lighter dark
                else:
                    base_color = (120, 120, 120)
                    dark_color = (80, 80, 80)
                    light_color = (160, 160, 160)
            elif self.block_type == 'copper' or self.block_type == 'copper_ore':
                # Light green copper
                base_color = (144, 238, 144)  # Light green
                dark_color = (124, 218, 124)  # Slightly darker green
                light_color = (164, 255, 164)  # Lighter green
            else:  # dirt
                base_color = (139, 69, 19)
                dark_color = (101, 50, 14)
                light_color = (160, 82, 45)
            
            # Main block (now 2x2 for destroyable blocks)
            block_rect = pygame.Rect(screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, base_color, block_rect)
            
            # Top highlight (light)
            pygame.draw.line(screen, light_color, (screen_x, screen_y), (screen_x + BLOCK_SIZE - 1, screen_y), 2)
            pygame.draw.line(screen, light_color, (screen_x, screen_y), (screen_x, screen_y + BLOCK_SIZE - 1), 2)
            
            # Bottom shadow (dark)
            pygame.draw.line(screen, dark_color, (screen_x + BLOCK_SIZE - 1, screen_y), 
                           (screen_x + BLOCK_SIZE - 1, screen_y + BLOCK_SIZE - 1), 2)
            pygame.draw.line(screen, dark_color, (screen_x, screen_y + BLOCK_SIZE - 1), 
                           (screen_x + BLOCK_SIZE - 1, screen_y + BLOCK_SIZE - 1), 2)
            
            # Border
            pygame.draw.rect(screen, (40, 40, 40), block_rect, 1)