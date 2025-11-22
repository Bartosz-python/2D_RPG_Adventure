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
        
        # ============================================
        # ZMIANA WIELKOŚCI BUDYNKÓW - TUTAJ:
        # ============================================
        # Buildings are larger than single tiles - 200% bigger (3x original size)
        # All buildings have the same size as witch (TILE_SIZE * 9)
        self.width = TILE_SIZE * 9  # 200% bigger = 3x (was 3, now 9) = 288 pixels
        self.height = TILE_SIZE * 9  # 288 pixels
        
        # ============================================
        # ZMIANA POZYCJI BUDYNKÓW - TUTAJ:
        # ============================================
        # Align TOP edge of building image to TOP edge of green ground block
        # Ground block top edge is at: ground_y = 25 * TILE_SIZE
        ground_y = 19 * TILE_SIZE  # Top edge of green ground block
        building_top_y = ground_y  # Top of building aligns with top of ground
        
        self.rect = pygame.Rect(
            x * TILE_SIZE,
            building_top_y,  # Top of building at top of ground block
            self.width,
            self.height
        )
    
    def is_player_near(self, player_rect):
        """Check if player is close enough to interact"""
        return self.rect.colliderect(player_rect.inflate(TILE_SIZE, TILE_SIZE))
    
    def render(self, screen, camera_x, camera_y):
        """Render building"""
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Try to load sprite first, fallback to colored rectangle
        sprite_name = f'building_{self.building_type}'
        sprite = self.asset_manager.get_sprite(sprite_name)
        
        if sprite:
            # ============================================
            # ZMIANA SKALOWANIA OBRAZKÓW BUDYNKÓW - TUTAJ:
            # ============================================
            # Scale sprite to building size (all buildings same size: TILE_SIZE * 9 = 288x288)
            sprite = pygame.transform.scale(sprite, (self.width, self.height))
            
            # ============================================
            # ZMIANA POZYCJI OBRAZKÓW BUDYNKÓW - TUTAJ:
            # ============================================
            # screen_x, screen_y are already calculated to align top of building with top of ground
            screen.blit(sprite, (screen_x, screen_y))
        else:
            # Fallback to colored rectangle rendering
            base_color = self._get_building_color()
            
            # Create darker and lighter shades
            dark_color = tuple(max(0, c - 40) for c in base_color)
            light_color = tuple(min(255, c + 40) for c in base_color)
            
            # Draw shadow
            shadow_offset = 4
            shadow_rect = pygame.Rect(screen_x + shadow_offset, screen_y + self.height - shadow_offset, 
                                     self.width, shadow_offset)
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 150))
            screen.blit(shadow_surface, shadow_rect)
            
            # Main building body
            building_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
            pygame.draw.rect(screen, base_color, building_rect)
            
            # Top highlight
            highlight_rect = pygame.Rect(screen_x, screen_y, self.width, self.height // 4)
            pygame.draw.rect(screen, light_color, highlight_rect)
            
            # Side shadow
            shadow_side = pygame.Rect(screen_x + self.width - 4, screen_y, 4, self.height)
            pygame.draw.rect(screen, dark_color, shadow_side)
            
            # Border
            pygame.draw.rect(screen, (30, 30, 30), building_rect, 3)
            
            # Draw door (simple rectangle)
            door_width = self.width // 3
            door_height = self.height // 2
            door_x = screen_x + (self.width - door_width) // 2
            door_y = screen_y + self.height - door_height
            pygame.draw.rect(screen, dark_color, (door_x, door_y, door_width, door_height))
            pygame.draw.rect(screen, (20, 20, 20), (door_x, door_y, door_width, door_height), 2)
        
        # Draw label with background (always show label)
        font = pygame.font.Font(None, 18)
        text = font.render(self.building_type.upper(), True, WHITE)
        text_rect = text.get_rect(center=(screen_x + self.width // 2, screen_y + self.height // 3))
        
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
            BUILDING_WITCH: (150, 50, 150),
            BUILDING_FIREPLACE: (200, 100, 0)
        }
        return colors.get(self.building_type, (100, 100, 100))