"""
src/ui/inventory_ui.py
Inventory display component
"""
import pygame
from src.config.settings import *

class InventoryUI:
    def __init__(self, x, y, asset_manager):
        self.x = x
        self.y = y
        self.asset_manager = asset_manager
        self.slot_size = 50
        self.slot_padding = 5
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def render(self, screen, inventory):
        """Render inventory UI"""
        # Title
        title = self.font.render("Inventory", True, WHITE)
        screen.blit(title, (self.x, self.y))
        
        y_offset = self.y + 30
        
        # Draw visible slots
        visible_items = inventory.get_visible_items()
        for i, (item, count) in enumerate(visible_items):
            slot_x = self.x + (self.slot_size + self.slot_padding) * i
            
            # Slot background
            slot_rect = pygame.Rect(slot_x, y_offset, self.slot_size, self.slot_size)
            pygame.draw.rect(screen, DARK_GRAY, slot_rect)
            pygame.draw.rect(screen, LIGHT_GRAY, slot_rect, 2)
            
            # Item
            if item:
                item_color = self._get_item_color(item)
                item_rect = pygame.Rect(slot_x + 5, y_offset + 5, self.slot_size - 10, self.slot_size - 10)
                pygame.draw.rect(screen, item_color, item_rect)
                
                # Count
                count_text = self.small_font.render(str(count), True, WHITE)
                screen.blit(count_text, (slot_x + self.slot_size - 20, y_offset + self.slot_size - 20))
        
        # Full message
        if inventory.is_full():
            msg = self.small_font.render("INVENTORY FULL", True, RED)
            screen.blit(msg, (self.x, y_offset + self.slot_size + 10))
    
    def _get_item_color(self, item):
        """Get color for item type"""
        colors = {
            'stone': GRAY,
            'dirt': (139, 69, 19),
            'wood': (101, 67, 33),
            'iron': (192, 192, 192),
            'gold_ore': YELLOW,
            'coin': YELLOW
        }
        return colors.get(item, WHITE)
    
    def handle_click(self, pos, inventory):
        """Handle click on inventory slot"""
        y_offset = self.y + 30
        for i in range(VISIBLE_SLOTS):
            slot_x = self.x + (self.slot_size + self.slot_padding) * i
            slot_rect = pygame.Rect(slot_x, y_offset, self.slot_size, self.slot_size)
            if slot_rect.collidepoint(pos):
                return i
        return None