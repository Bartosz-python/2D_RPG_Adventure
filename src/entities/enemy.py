"""
src/entities/enemy.py
Enemy AI and behavior
"""
import pygame
from src.config.settings import *
from src.entities.entity import Entity

class Enemy(Entity):
    def __init__(self, x, y, enemy_type, asset_manager, sprite_path=None):
        # Get stats from enemy type
        stats = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES['goblin'])
        
        # Initialize base entity
        super().__init__(x, y, TILE_SIZE, TILE_SIZE * 2)
        
        self.enemy_type = enemy_type
        self.asset_manager = asset_manager
        self.sprite_path = sprite_path  # Custom sprite path for graphics
        
        # Stats from config
        self.max_hp = stats['hp']
        self.hp = self.max_hp
        self.damage = stats['damage']
        self.speed = stats['speed']
        self.coin_value = stats['coins']
        
        # AI state
        self.state = 'idle'
        self.target = None
        self.attack_cooldown = 0
        self.aggro_range = 300
        self.attack_range = TILE_SIZE * 2
        
        # Movement AI
        self.patrol_timer = 0
        self.patrol_direction = 1
        self.idle_timer = 0
    
    def update(self, dt, player, game_map):
        """Update enemy AI and physics"""
        if not self.is_alive():
            return
        
        # Calculate distance to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5
        
        # AI behavior based on distance
        if distance < self.attack_range:
            # Attack player
            self.state = 'attacking'
            self.attack_player(player, dt)
        elif distance < self.aggro_range:
            # Chase player
            self.state = 'chasing'
            self.chase_player(dx, dy, distance)
        else:
            # Patrol or idle
            self.state = 'patrol'
            self.patrol(dt)
        
        # Apply horizontal movement
        self.rect.x += self.velocity_x * dt
        self.handle_collision(game_map, 'x')
        
        # Apply gravity
        self.apply_gravity(dt)
        
        # Apply vertical movement
        self.rect.y += self.velocity_y * dt
        self.on_ground = False
        self.handle_collision(game_map, 'y')
        
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
    
    def chase_player(self, dx, dy, distance):
        """Chase the player"""
        # Move toward player horizontally
        if abs(dx) > TILE_SIZE // 2:
            if dx > 0:
                self.velocity_x = self.speed
                self.facing_right = True
            else:
                self.velocity_x = -self.speed
                self.facing_right = False
        else:
            self.velocity_x = 0
        
        # Jump if player is above and close
        if dy < -TILE_SIZE and abs(dx) < TILE_SIZE * 3 and self.on_ground:
            self.velocity_y = PLAYER_JUMP_VELOCITY * 0.8
    
    def attack_player(self, player, dt):
        """Attack the player"""
        self.velocity_x = 0
        
        if self.attack_cooldown <= 0:
            player.take_damage(self.damage)
            self.attack_cooldown = ENEMY_ATTACK_COOLDOWN
    
    def patrol(self, dt):
        """Patrol back and forth"""
        self.patrol_timer += dt
        
        # Change direction every 3 seconds
        if self.patrol_timer > 3.0:
            self.patrol_timer = 0
            self.patrol_direction *= -1
        
        # Patrol speed is half of chase speed
        self.velocity_x = self.speed * 0.5 * self.patrol_direction
        self.facing_right = self.patrol_direction > 0
    
    def take_damage(self, damage):
        """Take damage and trigger aggro"""
        super().take_damage(damage)
        # Become aggressive when hit
        self.aggro_range = 500
    
    def render(self, screen, camera_x, camera_y):
        """Render enemy"""
        if not self.is_alive():
            return
        
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
            sprite = self.asset_manager.get_sprite(f'enemy_{self.enemy_type}') if self.asset_manager else None
        
        # Draw shadow
        shadow_rect = pygame.Rect(screen_x + 2, screen_y + self.rect.height - 3, self.rect.width - 4, 3)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 120))
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw sprite if available, otherwise use color-based placeholder
        if sprite:
            screen.blit(sprite, (screen_x, screen_y))
        else:
            # Get enemy color based on type
            color = self._get_enemy_color()
            
            # Draw enemy body
            pygame.draw.rect(screen, color, (screen_x, screen_y, self.rect.width, self.rect.height))
            
            # Draw facing indicator
            eye_x = screen_x + (self.rect.width - 5) if self.facing_right else screen_x + 5
            pygame.draw.circle(screen, WHITE, (eye_x, screen_y + 10), 3)
        
        # Draw HP bar above enemy
        self._render_hp_bar(screen, screen_x, screen_y)
        
        # Draw state indicator (debug)
        if self.state == 'attacking':
            pygame.draw.circle(screen, RED, (screen_x + self.rect.width // 2, screen_y - 5), 3)
    
    def _render_hp_bar(self, screen, screen_x, screen_y):
        """Render HP bar above enemy"""
        hp_bar_width = TILE_SIZE
        hp_bar_height = 4
        hp_percentage = self.hp / self.max_hp
        
        # Background
        pygame.draw.rect(screen, HP_BAR_BG, 
                        (screen_x, screen_y - 10, hp_bar_width, hp_bar_height))
        # HP
        pygame.draw.rect(screen, HP_BAR_COLOR,
                        (screen_x, screen_y - 10, int(hp_bar_width * hp_percentage), hp_bar_height))
    
    def _get_enemy_color(self):
        """Get color based on enemy type"""
        colors = {
            'goblin': (0, 200, 0),      # Green
            'skeleton': (220, 220, 220), # White/gray
            'orc': (150, 0, 0)          # Dark red
        }
        return colors.get(self.enemy_type, RED)


class Boss(Enemy):
    """Boss enemy with enhanced stats and abilities"""
    
    def __init__(self, x, y, boss_type, asset_manager):
        super().__init__(x, y, boss_type, asset_manager)
        
        # Boss enhancements
        self.max_hp *= 5
        self.hp = self.max_hp
        self.damage *= 2
        self.coin_value *= 10
        self.attack_range = TILE_SIZE * 3
        
        # Special abilities
        self.special_cooldown = 0
        self.special_duration = 5.0
    
    def update(self, dt, player, game_map):
        """Update boss with special abilities"""
        super().update(dt, player, game_map)
        
        # Special ability cooldown
        if self.special_cooldown > 0:
            self.special_cooldown -= dt
    
    def use_special_ability(self, player):
        """Use special boss ability"""
        if self.special_cooldown <= 0:
            # Example: area damage
            distance = ((player.rect.centerx - self.rect.centerx)**2 + 
                       (player.rect.centery - self.rect.centery)**2)**0.5
            
            if distance < TILE_SIZE * 5:
                player.take_damage(self.damage * 2)
            
            self.special_cooldown = self.special_duration
    
    def render(self, screen, camera_x, camera_y):
        """Render boss (larger)"""
        if not self.is_alive():
            return
        
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Draw larger with crown indicator
        pygame.draw.rect(screen, (100, 0, 100), (screen_x, screen_y, self.rect.width, self.rect.height))
        pygame.draw.polygon(screen, YELLOW, [
            (screen_x + self.rect.width // 2, screen_y - 10),
            (screen_x + self.rect.width // 2 - 5, screen_y),
            (screen_x + self.rect.width // 2 + 5, screen_y)
        ])
        
        self._render_hp_bar(screen, screen_x, screen_y)