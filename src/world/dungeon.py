"""
src/world/dungeon.py
Dungeon generation and management
"""
import random
import pygame
from src.config.settings import *
from src.world.block import Block
from src.entities.enemy import Enemy

class Dungeon:
    def __init__(self, width, height, asset_manager, difficulty=1):
        self.width = width
        self.height = height
        self.asset_manager = asset_manager
        self.difficulty = difficulty
        
        self.blocks = []
        self.enemies = []
        self.entrance = None
        self.exit = None
        self.rooms = []
        
        self.generate()
    
    def generate(self):
        """Generate dungeon layout"""
        # Create floor and walls
        self._create_borders()
        
        # Generate rooms
        num_rooms = random.randint(3 + self.difficulty, 6 + self.difficulty)
        for _ in range(num_rooms):
            self._create_room()
        
        # Connect rooms with corridors
        self._connect_rooms()
        
        # Place enemies
        self._spawn_enemies()
        
        # Set entrance and exit
        if self.rooms:
            self.entrance = self.rooms[0]['center']
            self.exit = self.rooms[-1]['center']
    
    def _create_borders(self):
        """Create dungeon walls"""
        # Floor
        for x in range(self.width):
            for y in range(self.height - 5, self.height):
                block = Block(x, y, 'stone', self.asset_manager, destructible=False)
                self.blocks.append(block)
        
        # Ceiling
        for x in range(self.width):
            for y in range(0, 2):
                block = Block(x, y, 'stone', self.asset_manager, destructible=False)
                self.blocks.append(block)
        
        # Side walls
        for y in range(self.height):
            # Left wall
            block = Block(0, y, 'stone', self.asset_manager, destructible=False)
            self.blocks.append(block)
            # Right wall
            block = Block(self.width - 1, y, 'stone', self.asset_manager, destructible=False)
            self.blocks.append(block)
    
    def _create_room(self):
        """Create a random room"""
        room_width = random.randint(4, 8)
        room_height = random.randint(3, 6)
        
        # Random position (avoiding borders)
        x = random.randint(2, self.width - room_width - 2)
        y = random.randint(3, self.height - room_height - 7)
        
        # Check if room overlaps with existing rooms
        new_room = {
            'x': x, 'y': y,
            'width': room_width,
            'height': room_height,
            'center': (x + room_width // 2, y + room_height // 2)
        }
        
        # Check for overlap
        for room in self.rooms:
            if self._rooms_overlap(new_room, room):
                return
        
        # Create room walls
        for rx in range(x, x + room_width):
            # Top and bottom walls
            block_top = Block(rx, y, 'stone', self.asset_manager, destructible=False)
            block_bottom = Block(rx, y + room_height - 1, 'stone', self.asset_manager, destructible=False)
            self.blocks.append(block_top)
            self.blocks.append(block_bottom)
        
        for ry in range(y, y + room_height):
            # Left and right walls
            block_left = Block(x, ry, 'stone', self.asset_manager, destructible=False)
            block_right = Block(x + room_width - 1, ry, 'stone', self.asset_manager, destructible=False)
            self.blocks.append(block_left)
            self.blocks.append(block_right)
        
        self.rooms.append(new_room)
    
    def _rooms_overlap(self, room1, room2, padding=2):
        """Check if two rooms overlap"""
        return not (
            room1['x'] + room1['width'] + padding < room2['x'] or
            room1['x'] > room2['x'] + room2['width'] + padding or
            room1['y'] + room1['height'] + padding < room2['y'] or
            room1['y'] > room2['y'] + room2['height'] + padding
        )
    
    def _connect_rooms(self):
        """Connect rooms with corridors"""
        for i in range(len(self.rooms) - 1):
            room1 = self.rooms[i]
            room2 = self.rooms[i + 1]
            
            # Create L-shaped corridor
            cx1, cy1 = room1['center']
            cx2, cy2 = room2['center']
            
            # Horizontal corridor
            if cx1 < cx2:
                for x in range(cx1, cx2):
                    self._clear_block(x, cy1)
            else:
                for x in range(cx2, cx1):
                    self._clear_block(x, cy1)
            
            # Vertical corridor
            if cy1 < cy2:
                for y in range(cy1, cy2):
                    self._clear_block(cx2, y)
            else:
                for y in range(cy2, cy1):
                    self._clear_block(cx2, y)
    
    def _clear_block(self, x, y):
        """Remove block at position"""
        self.blocks = [b for b in self.blocks if not (b.grid_x == x and b.grid_y == y)]
    
    def _spawn_enemies(self):
        """Spawn enemies in rooms"""
        enemy_types = list(ENEMY_TYPES.keys())
        
        # Skip first room (player spawn)
        for room in self.rooms[1:]:
            # Number of enemies based on difficulty
            num_enemies = random.randint(1, 2 + self.difficulty)
            
            for _ in range(num_enemies):
                # Random position in room
                x = random.randint(room['x'] + 1, room['x'] + room['width'] - 2)
                y = room['y'] + room['height'] - 2
                
                # Random enemy type
                enemy_type = random.choice(enemy_types)
                enemy = Enemy(x * TILE_SIZE, y * TILE_SIZE, enemy_type, self.asset_manager)
                self.enemies.append(enemy)
    
    def get_entrance_position(self):
        """Get dungeon entrance position"""
        if self.entrance:
            return (self.entrance[0] * TILE_SIZE, self.entrance[1] * TILE_SIZE)
        return (TILE_SIZE * 3, TILE_SIZE * 3)
    
    def get_exit_position(self):
        """Get dungeon exit position"""
        if self.exit:
            return (self.exit[0] * TILE_SIZE, self.exit[1] * TILE_SIZE)
        return (self.width * TILE_SIZE - TILE_SIZE * 3, TILE_SIZE * 3)