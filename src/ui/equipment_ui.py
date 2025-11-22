"""
src/ui/equipment_ui.py
Equipment display component
"""
import pygame
from src.config.settings import *

class EquipmentUI:
    def __init__(self, x, y, asset_manager):
        self.x = x
        self.y = y
        self.asset_manager = asset_manager
        self.slot_size = 50
        self.slot_padding = 5
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def render(self, screen, equipment):
        """Render equipment bar"""
        labels = ['Helmet', 'Chest', 'Legs', 'Boots', 'Cons.1', 'Cons.2', 'Weapon']
        slot_keys = ['helmet', 'chestplate', 'leggings', 'boots', 'consumable1', 'consumable2', 'weapon']
        
        for i, (label, key) in enumerate(zip(labels, slot_keys)):
            slot_x = self.x + (self.slot_size + self.slot_padding) * i
            
            # Slot
            slot_rect = pygame.Rect(slot_x, self.y, self.slot_size, self.slot_size)
            pygame.draw.rect(screen, DARK_GRAY, slot_rect)
            pygame.draw.rect(screen, LIGHT_GRAY, slot_rect, 2)
            
            # Equipped item
            equipped_item = equipment.get_item(key)
            if equipped_item:
                item_color = self._get_item_color(equipped_item)
                item_rect = pygame.Rect(slot_x + 5, self.y + 5, self.slot_size - 10, self.slot_size - 10)
                pygame.draw.rect(screen, item_color, item_rect)
            
            # Label
            label_text = self.small_font.render(label, True, WHITE)
            label_rect = label_text.get_rect(center=(slot_x + self.slot_size // 2, self.y - 10))
            screen.blit(label_text, label_rect)
    
    def _get_item_color(self, item):
        """Get color for item"""
        colors = {
            'sword': (192, 192, 192),
            'wand': (138, 43, 226),
            'bow': (139, 69, 19),
            'club': (101, 67, 33),
            'leather_helmet': (139, 69, 19),
            'iron_helmet': (192, 192, 192),
            'health_potion': RED
        }
        return colors.get(item, WHITE)