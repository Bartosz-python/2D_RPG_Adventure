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
        self._load_assets()
    
    def _load_assets(self):
        """Load all assets - try PNG files first, fallback to placeholders"""
        # Load building sprites
        self._load_building_sprites()
        
        # Load background
        self._load_background()
        
        # Placeholder sprites (will be replaced with actual images if PNGs not found)
        if 'player' not in self.sprites:
            self.sprites['player'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE, BLUE)
        if 'enemy' not in self.sprites:
            self.sprites['enemy'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE, RED)
        if 'block_stone' not in self.sprites:
            self.sprites['block_stone'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE, GRAY)
        if 'block_dirt' not in self.sprites:
            self.sprites['block_dirt'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE, (139, 69, 19))
        if 'coin' not in self.sprites:
            self.sprites['coin'] = self._create_placeholder_surface(16, 16, YELLOW)
    
    def _load_building_sprites(self):
        """Load building and campfire sprites from PNG files"""
        building_types = ['bedroom', 'smith', 'tailor', 'witch', 'fireplace']
        for building_type in building_types:
            sprite_name = f'building_{building_type}'
            # Try buildings folder first, then root sprites folder
            sprite_path = os.path.join(SPRITES_PATH, 'buildings', f'{building_type}.png')
            if not os.path.exists(sprite_path):
                sprite_path = os.path.join(SPRITES_PATH, f'{building_type}.png')
            self.load_sprite(sprite_name, sprite_path)
    
    def _load_background(self):
        """Load background images from PNG files"""
        # Load general background
        bg_path = os.path.join(SPRITES_PATH, 'background.png')
        if not os.path.exists(bg_path):
            alt_path = os.path.join(ASSETS_PATH, 'background.png')
            if os.path.exists(alt_path):
                bg_path = alt_path
        self.load_sprite('background', bg_path)
        
        # Load main base background (if exists, will be used for main map)
        bg_main_path = os.path.join(SPRITES_PATH, 'background_main.png')
        if not os.path.exists(bg_main_path):
            bg_main_path = os.path.join(SPRITES_PATH, 'background_main_base.png')
        if not os.path.exists(bg_main_path):
            bg_main_path = os.path.join(ASSETS_PATH, 'background_main.png')
        self.load_sprite('background_main', bg_main_path)
    
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