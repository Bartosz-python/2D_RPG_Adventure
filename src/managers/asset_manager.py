"""
src/managers/asset_manager.py
Asset loading and caching
"""
import pygame
import os
from src.config.settings import *

class AssetManager:
    def __init__(self):
        self.sprites = {}
        self.sounds = {}
        self.fonts = {}
        self._load_placeholder_assets()
    
    def _load_placeholder_assets(self):
        """Create placeholder assets for MVP"""
        # Placeholder sprites (will be replaced with actual images)
        self.sprites['player'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE * 2, BLUE)
        self.sprites['enemy'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE * 2, RED)
        self.sprites['block_stone'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE, GRAY)
        self.sprites['block_dirt'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE, (139, 69, 19))
        self.sprites['coin'] = self._create_placeholder_surface(16, 16, YELLOW)
        self.sprites['building'] = self._create_placeholder_surface(TILE_SIZE * 3, TILE_SIZE * 3, (100, 50, 0))
    
    def _create_placeholder_surface(self, width, height, color):
        """Create a colored rectangle as placeholder"""
        surface = pygame.Surface((width, height))
        surface.fill(color)
        return surface
    
    def load_sprite(self, name, path):
        """Load sprite from file"""
        if name not in self.sprites:
            try:
                self.sprites[name] = pygame.image.load(path).convert_alpha()
            except:
                print(f"Could not load sprite: {path}")
                self.sprites[name] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE, WHITE)
        return self.sprites[name]
    
    def get_sprite(self, name):
        """Get cached sprite"""
        return self.sprites.get(name, None)
    
    def load_sound(self, name, path):
        """Load sound from file"""
        if name not in self.sounds:
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except:
                print(f"Could not load sound: {path}")
        return self.sounds.get(name, None)
    
    def get_sound(self, name):
        """Get cached sound"""
        return self.sounds.get(name, None)