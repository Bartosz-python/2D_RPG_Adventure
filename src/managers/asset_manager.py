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
        self._load_assets()
    
    def _load_placeholder_assets(self):
        # Placeholder sprites (will be replaced with actual images)
        self.sprites['player'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE * 2, BLUE)
        self.sprites['enemy'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE * 2, RED)
        self.sprites['block_stone'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE, GRAY)
        self.sprites['block_dirt'] = self._create_placeholder_surface(TILE_SIZE, TILE_SIZE, (139, 69, 19))
        self.sprites['coin'] = self._create_placeholder_surface(16, 16, YELLOW)
        self.sprites['building'] = self._create_placeholder_surface(TILE_SIZE * 3, TILE_SIZE * 3, (100, 50, 0))
    
    def _load_assets(self):
        """Load actual asset files"""
        # Load dirt sprite from .png file
        dirt_path = os.path.join('assets', 'sprites', 'blocks', 'dirt.png')
        if os.path.exists(dirt_path):
            try:
                dirt_sprite = pygame.image.load(dirt_path).convert_alpha()
                self.sprites['block_dirt'] = dirt_sprite
                self.sprites['dirt'] = dirt_sprite  # Also add as 'dirt' for inventory
            except Exception as e:
                print(f"Could not load dirt sprite from {dirt_path}: {e}")
        
        # Load stone sprite from .png file
        stone_path = os.path.join('assets', 'sprites', 'blocks', 'stone.png')
        if os.path.exists(stone_path):
            try:
                stone_sprite = pygame.image.load(stone_path).convert_alpha()
                self.sprites['block_stone'] = stone_sprite
                self.sprites['stone'] = stone_sprite  # Also add as 'stone' for inventory
            except Exception as e:
                print(f"Could not load stone sprite from {stone_path}: {e}")
        
        # Load building sprites
        building_types = ['bedroom', 'fireplace', 'smith', 'tailor', 'witch']
        for building_type in building_types:
            building_path = os.path.join('assets', 'sprites', 'buildings', f'{building_type}.png')
            if os.path.exists(building_path):
                try:
                    building_sprite = pygame.image.load(building_path).convert_alpha()
                    self.sprites[f'building_{building_type}'] = building_sprite
                except Exception as e:
                    print(f"Could not load building sprite from {building_path}: {e}")
        
        # Load main map background
        background_path = os.path.join('assets', 'sprites', 'background_main.png')
        if os.path.exists(background_path):
            try:
                background_sprite = pygame.image.load(background_path).convert()
                self.sprites['background_main'] = background_sprite
            except Exception as e:
                print(f"Could not load main map background from {background_path}: {e}")
        
        # Load additional background layer (foreground layer)
        background_layer2_path = os.path.join('assets', 'sprites', 'ground.png')
        if os.path.exists(background_layer2_path):
            try:
                background_layer2_sprite = pygame.image.load(background_layer2_path).convert_alpha()
                self.sprites['background_layer2'] = background_layer2_sprite
            except Exception as e:
                print(f"Could not load background layer 2 from {background_layer2_path}: {e}")
    
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