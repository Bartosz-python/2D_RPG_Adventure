"""
src/entities/enemy.py
Enemy AI and behavior
"""
import pygame
from src.config.settings import *

class Enemy:
    def __init__(self, x, y, enemy_type, asset_manager, sprite_path=None):
        self.enemy_type = enemy_type
        self.asset_manager = asset_manager
        self.sprite_path = sprite_path  # Custom sprite path for graphics
        
        # Get stats from enemy type
        stats = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES['goblin'])
        self.max_hp = stats['hp']
        self.hp = self.max_hp
        self.damage = stats['damage']
        self.speed = stats['speed']
        self.coin_value = stats['coins']
        
        # Position and collision
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE * 2)
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        
        # AI state
        self.state = 'idle'
        self.target = None
        self.attack_cooldown = 0
    
    def update(self, dt, player, game_map):
        """Update enemy AI and physics"""
        # Simple AI: move toward player if in range
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5
        
        if distance < 300:  # Aggro range
            # Move toward player
            if abs(dx) > TILE_SIZE:
                self.velocity_x = self.speed if dx > 0 else -self.speed
            else:
                self.velocity_x = 0
            
            # Attack if close enough (but not if player is attacking - give player priority)
            if distance < TILE_SIZE * 2 and self.attack_cooldown <= 0 and not player.is_attacking:
                player.take_damage(self.damage)
                self.attack_cooldown = ENEMY_ATTACK_COOLDOWN
        else:
            self.velocity_x = 0
        
        # Apply movement
        self.rect.x += self.velocity_x * dt
        self.handle_collision(game_map, 'x')
        
        # Apply gravity
        self.velocity_y += GRAVITY * dt
        self.velocity_y = min(self.velocity_y, 1000)
        
        self.rect.y += self.velocity_y * dt
        self.on_ground = False
        self.handle_collision(game_map, 'y')
        
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
    
    def handle_collision(self, game_map, axis):
        """Handle collision with map"""
        collided_blocks = game_map.get_colliding_blocks(self.rect)
        
        for block in collided_blocks:
            if axis == 'x':
                if self.velocity_x > 0:
                    self.rect.right = block.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = block.rect.right
            elif axis == 'y':
                if self.velocity_y > 0:
                    self.rect.bottom = block.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = block.rect.bottom
                    self.velocity_y = 0
    
    def take_damage(self, damage):
        """Take damage"""
        self.hp -= damage
    
    def render(self, screen, camera_x, camera_y):
        """Render enemy"""
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Try to load custom sprite if path provided
        sprite = None
        if self.sprite_path:
            try:
                sprite = pygame.image.load(self.sprite_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (self.rect.width, self.rect.height))
            except:
                sprite = None
        
        # If no custom sprite, try asset manager
        if not sprite:
            sprite = self.asset_manager.get_sprite(f'enemy_{self.enemy_type}')
        
        # Draw shadow
        shadow_rect = pygame.Rect(screen_x + 2, screen_y + self.rect.height - 3, self.rect.width - 4, 3)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 120))
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw sprite if available, otherwise use placeholder
        if sprite:
            screen.blit(sprite, (screen_x, screen_y))
        else:
            # Draw enemy body with gradient (placeholder)
            base_color = (200, 50, 50)  # Dark red
            highlight_color = (255, 100, 100)  # Light red
            
            # Main body
            enemy_rect = pygame.Rect(screen_x, screen_y, self.rect.width, self.rect.height)
            pygame.draw.rect(screen, base_color, enemy_rect)
            
            # Highlight
            highlight_rect = pygame.Rect(screen_x, screen_y, self.rect.width, self.rect.height // 3)
            pygame.draw.rect(screen, highlight_color, highlight_rect)
            
            # Border
            pygame.draw.rect(screen, (30, 30, 30), enemy_rect, 2)
            
            # Draw eyes (red glowing)
            eye_y = screen_y + self.rect.height // 3
            pygame.draw.circle(screen, (255, 200, 200), (screen_x + self.rect.width // 3, eye_y), 3)
            pygame.draw.circle(screen, (255, 200, 200), (screen_x + 2 * self.rect.width // 3, eye_y), 3)
            pygame.draw.circle(screen, (255, 0, 0), (screen_x + self.rect.width // 3, eye_y), 2)
            pygame.draw.circle(screen, (255, 0, 0), (screen_x + 2 * self.rect.width // 3, eye_y), 2)
        
        # Draw HP bar above enemy
        hp_bar_width = TILE_SIZE
        hp_bar_height = 5
        hp_percentage = max(0, self.hp / self.max_hp)
        
        # Background
        hp_bg_rect = pygame.Rect(screen_x, screen_y - 12, hp_bar_width, hp_bar_height)
        pygame.draw.rect(screen, (40, 40, 40), hp_bg_rect)
        pygame.draw.rect(screen, (60, 60, 60), hp_bg_rect, 1)
        
        # HP
        if hp_percentage > 0:
            hp_rect = pygame.Rect(screen_x, screen_y - 12, int(hp_bar_width * hp_percentage), hp_bar_height)
            # Gradient HP bar
            hp_color = (220, 20, 60) if hp_percentage > 0.5 else (255, 100, 50)
            pygame.draw.rect(screen, hp_color, hp_rect)