"""
src/world/building.py
Building interaction class
"""
import pygame
from src.config.settings import *

class Building:
    def __init__(self, x, y, building_type, asset_manager):
        self.grid_x = x
        self.grid_y = y
        self.building_type = building_type
        self.asset_manager = asset_manager
        
        # Render size is 3x (for larger images)
        self.render_width = TILE_SIZE * 9
        self.render_height = TILE_SIZE * 9
        
        # Interaction rect is original size (for proper interaction range)
        self.interaction_width = TILE_SIZE * 3
        self.interaction_height = TILE_SIZE * 3
        
        # Calculate interaction center from grid position
        # Interaction area is centered at grid position, offset 40px to the right
        interaction_center_x = x * TILE_SIZE + self.interaction_width / 2 + 40
        interaction_center_y = y * TILE_SIZE + self.interaction_height / 2
        
        # Position building's visual center to match interaction center (minus the 40px offset)
        # So building visual center = interaction center - 40px
        building_visual_center_x = interaction_center_x - 40
        building_visual_center_y = interaction_center_y
        
        # Calculate render position from visual center
        self.render_offset_x = building_visual_center_x - (self.render_width / 2) - (x * TILE_SIZE)
        self.render_offset_y = building_visual_center_y - (self.render_height / 2) - (y * TILE_SIZE)
        
        # Interaction rect centered at grid position, offset 40px right
        interaction_x = x * TILE_SIZE + 40
        interaction_y = y * TILE_SIZE
        
        self.rect = pygame.Rect(
            interaction_x,
            interaction_y,
            self.interaction_width,
            self.interaction_height
        )
    
    def is_player_near(self, player_rect):
        """Check if player is close enough to interact"""
        return self.rect.colliderect(player_rect.inflate(TILE_SIZE, TILE_SIZE))
    
    def render(self, screen, camera_x, camera_y):
        """Render building"""
        # Render position: offset by render_offset_x and render_offset_y to center on interaction
        base_x = self.grid_x * TILE_SIZE
        base_y = self.grid_y * TILE_SIZE
        render_x = base_x + self.render_offset_x - camera_x
        render_y = base_y + self.render_offset_y - camera_y
        
        # Try to get building sprite from asset manager
        sprite = self.asset_manager.get_sprite(f'building_{self.building_type}')
        
        if sprite:
            # Scale sprite to render size (3x)
            if sprite.get_size() != (self.render_width, self.render_height):
                sprite = pygame.transform.scale(sprite, (self.render_width, self.render_height))
            
            # Draw sprite (shadow removed)
            screen.blit(sprite, (render_x, render_y))
        elif self.building_type != BUILDING_FIREPLACE:
            # Fallback to colored rectangle rendering (fireplace always uses sprite, no placeholder)
            # Get base color
            base_color = self._get_building_color()
            
            # Create darker and lighter shades
            dark_color = tuple(max(0, c - 40) for c in base_color)
            light_color = tuple(min(255, c + 40) for c in base_color)
            
            # Main building body (shadow removed) - use render size
            building_rect = pygame.Rect(render_x, render_y, self.render_width, self.render_height)
            pygame.draw.rect(screen, base_color, building_rect)
            
            # Top highlight
            highlight_rect = pygame.Rect(render_x, render_y, self.render_width, self.render_height // 4)
            pygame.draw.rect(screen, light_color, highlight_rect)
            
            # Side shadow
            shadow_side = pygame.Rect(render_x + self.render_width - 4, render_y, 4, self.render_height)
            pygame.draw.rect(screen, dark_color, shadow_side)
            
            # Border
            pygame.draw.rect(screen, (30, 30, 30), building_rect, 3)
            
            # Draw door (simple rectangle)
            door_width = self.render_width // 3
            door_height = self.render_height // 2
            door_x = render_x + (self.render_width - door_width) // 2
            door_y = render_y + self.render_height - door_height
            pygame.draw.rect(screen, dark_color, (door_x, door_y, door_width, door_height))
            pygame.draw.rect(screen, (20, 20, 20), (door_x, door_y, door_width, door_height), 2)
        
        # Draw label with background (always show label) - centered on render position
        font = pygame.font.Font(None, 18)
        text = font.render(self.building_type.upper(), True, WHITE)
        
        # Adjust text position based on building type
        if self.building_type == BUILDING_FIREPLACE:
            # Position text below the building asset
            text_rect = text.get_rect(center=(render_x + self.render_width // 2, render_y + self.render_height + TILE_SIZE))
        else:
            text_y_offset = 0
            if self.building_type == BUILDING_BEDROOM or self.building_type == BUILDING_TAILOR:
                text_y_offset = -TILE_SIZE  # Move 1 block higher
            elif self.building_type == BUILDING_WITCH:
                text_y_offset = -TILE_SIZE * 2  # Move 2 blocks higher
            
            text_rect = text.get_rect(center=(render_x + self.render_width // 2, render_y + self.render_height // 3 + text_y_offset))
        
        # Text background
        bg_rect = text_rect.inflate(8, 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        screen.blit(bg_surface, bg_rect)
        screen.blit(text, text_rect)
    
    def _get_building_color(self):
        """Get color based on building type"""
        colors = {
            BUILDING_BEDROOM: (100, 50, 150),
            BUILDING_SMITH: (150, 50, 50),
            BUILDING_TAILOR: (50, 150, 50),
            BUILDING_WITCH: (150, 50, 150)
        }
        return colors.get(self.building_type, (100, 100, 100))