"""
src/ui/menu.py
Building menu component
"""
import pygame
from src.config.settings import *

class BuildingMenu:
    def __init__(self, building_type, asset_manager):
        self.building_type = building_type
        self.asset_manager = asset_manager
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.menu_width = 500
        self.menu_height = 400
        self.menu_x = SCREEN_WIDTH // 2 - self.menu_width // 2
        self.menu_y = SCREEN_HEIGHT // 2 - self.menu_height // 2
    
    def render(self, screen, player):
        """Render menu"""
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Menu box
        pygame.draw.rect(screen, DARK_GRAY, (self.menu_x, self.menu_y, self.menu_width, self.menu_height))
        pygame.draw.rect(screen, WHITE, (self.menu_x, self.menu_y, self.menu_width, self.menu_height), 3)
        
        # Title
        title = self.font.render(f"{self.building_type.upper()}", True, WHITE)
        screen.blit(title, (self.menu_x + 20, self.menu_y + 20))
        
        # Content
        if self.building_type == BUILDING_SMITH:
            self._render_smith(screen, player)
        elif self.building_type == BUILDING_TAILOR:
            self._render_tailor(screen, player)
        elif self.building_type == BUILDING_WITCH:
            self._render_witch(screen, player)
        elif self.building_type == BUILDING_FIREPLACE:
            self._render_fireplace(screen, player)
        elif self.building_type == BUILDING_BEDROOM:
            self._render_bedroom(screen, player)
        
        # Close instruction
        close_text = self.small_font.render("Press ESC to close", True, LIGHT_GRAY)
        screen.blit(close_text, (self.menu_x + 20, self.menu_y + self.menu_height - 30))
    
    def _render_smith(self, screen, player):
        """Render smith menu"""
        y = self.menu_y + 70
        text = self.small_font.render("Weapon Upgrades:", True, WHITE)
        screen.blit(text, (self.menu_x + 30, y))
        
        upgrades = [
            ("Iron Sword", 100, 20),
            ("Steel Sword", 250, 30),
            ("Legendary Sword", 500, 45)
        ]
        
        y += 40
        for name, cost, damage in upgrades:
            text = self.small_font.render(f"{name} - {cost}g (DMG: {damage})", True, LIGHT_GRAY)
            screen.blit(text, (self.menu_x + 50, y))
            y += 35
    
    def _render_tailor(self, screen, player):
        """Render tailor menu"""
        y = self.menu_y + 70
        text = self.small_font.render("Armor & Backpack:", True, WHITE)
        screen.blit(text, (self.menu_x + 30, y))
        
        items = [
            ("Leather Armor Set", 150),
            ("Iron Armor Set", 400),
            ("Backpack Upgrade (+6 slots)", 200)
        ]
        
        y += 40
        for name, cost in items:
            text = self.small_font.render(f"{name} - {cost}g", True, LIGHT_GRAY)
            screen.blit(text, (self.menu_x + 50, y))
            y += 35
    
    def _render_witch(self, screen, player):
        """Render witch menu"""
        y = self.menu_y + 70
        text = self.small_font.render("Potions & Consumables:", True, WHITE)
        screen.blit(text, (self.menu_x + 30, y))
        
        items = [
            ("Health Potion", 20),
            ("Strength Potion", 30),
            ("Speed Potion", 25)
        ]
        
        y += 40
        for name, cost in items:
            text = self.small_font.render(f"{name} - {cost}g", True, LIGHT_GRAY)
            screen.blit(text, (self.menu_x + 50, y))
            y += 35
    
    def _render_fireplace(self, screen, player):
        """Render fireplace menu"""
        y = self.menu_y + 70
        text = self.small_font.render("Cook Food:", True, WHITE)
        screen.blit(text, (self.menu_x + 30, y))
        
        recipes = [
            "Raw Meat → Cooked Meat",
            "Fish → Grilled Fish",
            "Wheat → Bread"
        ]
        
        y += 40
        for recipe in recipes:
            text = self.small_font.render(recipe, True, LIGHT_GRAY)
            screen.blit(text, (self.menu_x + 50, y))
            y += 35
    
    def _render_bedroom(self, screen, player):
        """Render bedroom menu"""
        y = self.menu_y + 70
        text = self.small_font.render("Rest & Save", True, WHITE)
        screen.blit(text, (self.menu_x + 30, y))
        
        y += 50
        save_text = self.small_font.render("Press S to save your progress", True, GREEN)
        screen.blit(save_text, (self.menu_x + 50, y))
        
        y += 40
        rest_text = self.small_font.render("Press R to rest (restore HP)", True, GREEN)
        screen.blit(rest_text, (self.menu_x + 50, y))