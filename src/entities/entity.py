"""
src/entities/entity.py
Base entity class for all game entities
"""
import pygame
from src.config.settings import *

class Entity:
    """Base class for all entities (player, enemies, etc.)"""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.alive = True
        
        # Stats
        self.hp = 100
        self.max_hp = 100
        self.speed = 100
        
        # Visual
        self.facing_right = True
        self.sprite = None
    
    def update(self, dt, game_map):
        """Update entity - override in subclasses"""
        pass
    
    def apply_gravity(self, dt):
        """Apply gravity to entity"""
        self.velocity_y += GRAVITY * dt
        self.velocity_y = min(self.velocity_y, 1000)  # Terminal velocity
    
    def move(self, dt):
        """Apply velocity to position"""
        self.rect.x += self.velocity_x * dt
        self.rect.y += self.velocity_y * dt
    
    def handle_collision(self, game_map, axis):
        """Handle collision with map blocks"""
        collided_blocks = game_map.get_colliding_blocks(self.rect)
        
        for block in collided_blocks:
            if axis == 'x':
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = block.rect.left
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = block.rect.right
                self.velocity_x = 0
            
            elif axis == 'y':
                if self.velocity_y > 0:  # Falling
                    self.rect.bottom = block.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  # Jumping up
                    self.rect.top = block.rect.bottom
                    self.velocity_y = 0
    
    def take_damage(self, damage):
        """Take damage"""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
    
    def heal(self, amount):
        """Heal entity"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def is_alive(self):
        """Check if entity is alive"""
        return self.alive and self.hp > 0
    
    def render(self, screen, camera_x, camera_y):
        """Render entity - override in subclasses"""
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        pygame.draw.rect(screen, WHITE, (screen_x, screen_y, self.rect.width, self.rect.height))