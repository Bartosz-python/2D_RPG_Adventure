"""
src/entities/projectile.py
Projectile system for ranged weapons (bow, wand)
"""
import pygame
import math
from src.config.settings import *

class Projectile:
    """Base projectile class"""
    
    def __init__(self, x, y, target_x, target_y, speed, damage, projectile_type='arrow'):
        self.rect = pygame.Rect(x, y, 8, 8)
        self.damage = damage
        self.projectile_type = projectile_type
        self.active = True
        self.speed = speed
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = max(1, math.sqrt(dx**2 + dy**2))
        
        # Normalize and apply speed
        self.velocity_x = (dx / distance) * speed
        self.velocity_y = (dy / distance) * speed
        
        # Visual
        self.angle = math.atan2(dy, dx)
        self.lifetime = 5.0  # Seconds before despawn
        self.piercing = False  # Can hit multiple enemies
        self.gravity_affected = projectile_type == 'arrow'
    
    def update(self, dt, game_map):
        """Update projectile position"""
        if not self.active:
            return
        
        # Apply gravity to arrows
        if self.gravity_affected:
            self.velocity_y += GRAVITY * dt * 0.3  # Reduced gravity
        
        # Move
        self.rect.x += self.velocity_x * dt
        self.rect.y += self.velocity_y * dt
        
        # Update angle for rotation
        if self.velocity_x != 0 or self.velocity_y != 0:
            self.angle = math.atan2(self.velocity_y, self.velocity_x)
        
        # Lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
        
        # Check collision with blocks
        colliding_blocks = game_map.get_colliding_blocks(self.rect)
        if colliding_blocks:
            self.active = False
    
    def check_hit(self, target_rect):
        """Check if projectile hits target"""
        if not self.active:
            return False
        
        if self.rect.colliderect(target_rect):
            if not self.piercing:
                self.active = False
            return True
        return False
    
    def render(self, screen, camera_x, camera_y):
        """Render projectile"""
        if not self.active:
            return
        
        screen_x = self.rect.centerx - camera_x
        screen_y = self.rect.centery - camera_y
        
        # Get color based on type
        color = self._get_projectile_color()
        
        # Draw rotated projectile
        length = 12
        end_x = screen_x + math.cos(self.angle) * length
        end_y = screen_y + math.sin(self.angle) * length
        
        pygame.draw.line(screen, color, (screen_x, screen_y), (end_x, end_y), 3)
        pygame.draw.circle(screen, color, (int(end_x), int(end_y)), 2)
    
    def _get_projectile_color(self):
        """Get color based on projectile type"""
        colors = {
            'arrow': (139, 69, 19),      # Brown
            'magic': (138, 43, 226),     # Purple
            'fireball': (255, 69, 0),    # Red-orange
            'ice': (173, 216, 230)       # Light blue
        }
        return colors.get(self.projectile_type, WHITE)


class Arrow(Projectile):
    """Arrow projectile from bow"""
    
    def __init__(self, x, y, target_x, target_y, damage):
        super().__init__(x, y, target_x, target_y, speed=400, damage=damage, projectile_type='arrow')
        self.gravity_affected = True


class MagicBolt(Projectile):
    """Magic projectile from wand"""
    
    def __init__(self, x, y, target_x, target_y, damage):
        super().__init__(x, y, target_x, target_y, speed=500, damage=damage, projectile_type='magic')
        self.gravity_affected = False
        self.piercing = False
    
    def render(self, screen, camera_x, camera_y):
        """Render magic bolt with glow effect"""
        if not self.active:
            return
        
        screen_x = self.rect.centerx - camera_x
        screen_y = self.rect.centery - camera_y
        
        # Draw glow
        for i in range(3, 0, -1):
            alpha = 100 - i * 20
            color = (138, 43, 226)
            pygame.draw.circle(screen, color, (screen_x, screen_y), i * 3)
        
        # Draw core
        pygame.draw.circle(screen, WHITE, (screen_x, screen_y), 3)


class Fireball(Projectile):
    """Fireball with area damage"""
    
    def __init__(self, x, y, target_x, target_y, damage):
        super().__init__(x, y, target_x, target_y, speed=300, damage=damage, projectile_type='fireball')
        self.explosion_radius = TILE_SIZE * 2
        self.exploded = False
    
    def update(self, dt, game_map):
        """Update with explosion on impact"""
        old_active = self.active
        super().update(dt, game_map)
        
        # Trigger explosion when deactivated
        if old_active and not self.active and not self.exploded:
            self.explode()
    
    def explode(self):
        """Create explosion effect"""
        self.exploded = True
        # Explosion logic would go here
        # For now just mark as exploded
    
    def check_explosion_hit(self, target_rect):
        """Check if target is in explosion radius"""
        if not self.exploded:
            return False
        
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        return distance <= self.explosion_radius
    
    def render(self, screen, camera_x, camera_y):
        """Render fireball with trail"""
        if not self.active and not self.exploded:
            return
        
        screen_x = self.rect.centerx - camera_x
        screen_y = self.rect.centery - camera_y
        
        if self.exploded:
            # Draw explosion
            pygame.draw.circle(screen, (255, 69, 0), (screen_x, screen_y), 20)
            pygame.draw.circle(screen, (255, 140, 0), (screen_x, screen_y), 15)
            pygame.draw.circle(screen, (255, 255, 0), (screen_x, screen_y), 10)
        else:
            # Draw fireball
            pygame.draw.circle(screen, (255, 69, 0), (screen_x, screen_y), 6)
            pygame.draw.circle(screen, (255, 140, 0), (screen_x, screen_y), 4)


class ProjectileManager:
    """Manage all projectiles in the game"""
    
    def __init__(self):
        self.projectiles = []
    
    def add_projectile(self, projectile):
        """Add projectile to manager"""
        self.projectiles.append(projectile)
    
    def create_arrow(self, x, y, target_x, target_y, damage):
        """Create and add arrow"""
        arrow = Arrow(x, y, target_x, target_y, damage)
        self.add_projectile(arrow)
        return arrow
    
    def create_magic_bolt(self, x, y, target_x, target_y, damage):
        """Create and add magic bolt"""
        bolt = MagicBolt(x, y, target_x, target_y, damage)
        self.add_projectile(bolt)
        return bolt
    
    def create_fireball(self, x, y, target_x, target_y, damage):
        """Create and add fireball"""
        fireball = Fireball(x, y, target_x, target_y, damage)
        self.add_projectile(fireball)
        return fireball
    
    def update(self, dt, game_map):
        """Update all projectiles"""
        for projectile in self.projectiles[:]:
            projectile.update(dt, game_map)
            
            # Remove inactive projectiles
            if not projectile.active:
                self.projectiles.remove(projectile)
    
    def check_hits(self, targets):
        """Check projectile hits against targets"""
        hits = []
        for projectile in self.projectiles:
            for target in targets:
                if projectile.check_hit(target.rect):
                    target.take_damage(projectile.damage)
                    hits.append((projectile, target))
        return hits
    
    def render(self, screen, camera_x, camera_y):
        """Render all projectiles"""
        for projectile in self.projectiles:
            projectile.render(screen, camera_x, camera_y)
    
    def clear(self):
        """Clear all projectiles"""
        self.projectiles.clear()
    
    def get_active_count(self):
        """Get number of active projectiles"""
        return len(self.projectiles)