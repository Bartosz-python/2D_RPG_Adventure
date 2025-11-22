"""
src/core/physics.py
Physics engine for gravity, collision, and movement
"""
import pygame
from src.config.settings import *

class PhysicsEngine:
    """Handle physics calculations for entities"""
    
    def __init__(self, gravity=GRAVITY):
        self.gravity = gravity
    
    def apply_gravity(self, entity, dt):
        """Apply gravity to an entity"""
        entity.velocity_y += self.gravity * dt
        # Terminal velocity
        entity.velocity_y = min(entity.velocity_y, 1000)
    
    def apply_velocity(self, entity, dt):
        """Apply velocity to entity position"""
        entity.rect.x += entity.velocity_x * dt
        entity.rect.y += entity.velocity_y * dt
    
    def check_ground_collision(self, entity, blocks):
        """Check if entity is on ground"""
        # Create a small rect below entity to check for ground
        check_rect = pygame.Rect(
            entity.rect.x + 2,
            entity.rect.bottom,
            entity.rect.width - 4,
            2
        )
        
        for block in blocks:
            if check_rect.colliderect(block.rect):
                return True
        return False
    
    def resolve_collision(self, entity, block, axis):
        """Resolve collision between entity and block"""
        if axis == 'x':
            if entity.velocity_x > 0:  # Moving right
                entity.rect.right = block.rect.left
            elif entity.velocity_x < 0:  # Moving left
                entity.rect.left = block.rect.right
            entity.velocity_x = 0
        
        elif axis == 'y':
            if entity.velocity_y > 0:  # Falling
                entity.rect.bottom = block.rect.top
                entity.velocity_y = 0
                entity.on_ground = True
            elif entity.velocity_y < 0:  # Jumping
                entity.rect.top = block.rect.bottom
                entity.velocity_y = 0
    
    def resolve_entity_collision(self, entity1, entity2):
        """Resolve collision between two entities"""
        if not entity1.rect.colliderect(entity2.rect):
            return
        
        # Calculate overlap
        dx = entity1.rect.centerx - entity2.rect.centerx
        dy = entity1.rect.centery - entity2.rect.centery
        
        # Separate entities
        if abs(dx) > abs(dy):
            if dx > 0:
                entity1.rect.left = entity2.rect.right
            else:
                entity1.rect.right = entity2.rect.left
        else:
            if dy > 0:
                entity1.rect.top = entity2.rect.bottom
            else:
                entity1.rect.bottom = entity2.rect.top
    
    def apply_knockback(self, entity, source_pos, force=200):
        """Apply knockback force to entity"""
        dx = entity.rect.centerx - source_pos[0]
        dy = entity.rect.centery - source_pos[1]
        
        # Normalize
        distance = max(1, (dx**2 + dy**2)**0.5)
        dx /= distance
        dy /= distance
        
        # Apply force
        entity.velocity_x = dx * force
        entity.velocity_y = dy * force * 0.5  # Less vertical knockback
    
    def raycast(self, start_pos, end_pos, blocks):
        """Raycast from start to end, return first block hit"""
        # Simple line-stepping raycast
        steps = 50
        dx = (end_pos[0] - start_pos[0]) / steps
        dy = (end_pos[1] - start_pos[1]) / steps
        
        for i in range(steps):
            check_x = start_pos[0] + dx * i
            check_y = start_pos[1] + dy * i
            
            for block in blocks:
                if block.rect.collidepoint(check_x, check_y):
                    return block, (check_x, check_y)
        
        return None, end_pos
    
    def is_line_of_sight(self, start_pos, end_pos, blocks):
        """Check if there's a clear line of sight between two points"""
        block, _ = self.raycast(start_pos, end_pos, blocks)
        return block is None


class CollisionDetector:
    """Optimized collision detection"""
    
    def __init__(self, tile_size=TILE_SIZE):
        self.tile_size = tile_size
    
    def get_nearby_blocks(self, entity_rect, all_blocks, padding=2):
        """Get blocks near entity for collision checking"""
        # Calculate grid bounds
        left = max(0, (entity_rect.left // self.tile_size) - padding)
        right = (entity_rect.right // self.tile_size) + padding
        top = max(0, (entity_rect.top // self.tile_size) - padding)
        bottom = (entity_rect.bottom // self.tile_size) + padding
        
        # Filter blocks in range
        nearby = []
        for block in all_blocks:
            grid_x = block.rect.x // self.tile_size
            grid_y = block.rect.y // self.tile_size
            
            if left <= grid_x <= right and top <= grid_y <= bottom:
                nearby.append(block)
        
        return nearby
    
    def get_colliding_blocks(self, entity_rect, blocks):
        """Get all blocks colliding with entity"""
        return [block for block in blocks if entity_rect.colliderect(block.rect)]
    
    def check_collision_point(self, point, blocks):
        """Check if a point collides with any block"""
        for block in blocks:
            if block.rect.collidepoint(point):
                return block
        return None
    
    def get_collision_normal(self, rect1, rect2):
        """Get the normal vector of collision"""
        dx = rect1.centerx - rect2.centerx
        dy = rect1.centery - rect2.centery
        
        if abs(dx) > abs(dy):
            return (1 if dx > 0 else -1, 0)
        else:
            return (0, 1 if dy > 0 else -1)
    
    def sweep_test(self, rect, velocity, blocks):
        """Sweep test for continuous collision detection"""
        # Move rect along velocity and check for collisions
        test_rect = rect.copy()
        steps = 10
        step_x = velocity[0] / steps
        step_y = velocity[1] / steps
        
        for i in range(steps):
            test_rect.x += step_x
            test_rect.y += step_y
            
            for block in blocks:
                if test_rect.colliderect(block.rect):
                    return block, i / steps  # Return block and collision time
        
        return None, 1.0


class MovementController:
    """Handle entity movement with physics"""
    
    def __init__(self, physics_engine, collision_detector):
        self.physics = physics_engine
        self.collision = collision_detector
    
    def move_entity(self, entity, game_map, dt):
        """Move entity with physics and collision"""
        # Store old position
        old_x = entity.rect.x
        old_y = entity.rect.y
        
        # Apply horizontal movement
        entity.rect.x += entity.velocity_x * dt
        
        # Get nearby blocks for optimization
        nearby_blocks = self.collision.get_nearby_blocks(entity.rect, game_map.blocks)
        
        # Check horizontal collision
        colliding = self.collision.get_colliding_blocks(entity.rect, nearby_blocks)
        for block in colliding:
            self.physics.resolve_collision(entity, block, 'x')
        
        # Apply gravity
        self.physics.apply_gravity(entity, dt)
        
        # Apply vertical movement
        entity.rect.y += entity.velocity_y * dt
        entity.on_ground = False
        
        # Check vertical collision
        colliding = self.collision.get_colliding_blocks(entity.rect, nearby_blocks)
        for block in colliding:
            self.physics.resolve_collision(entity, block, 'y')
    
    def jump(self, entity, jump_velocity=PLAYER_JUMP_VELOCITY):
        """Make entity jump"""
        if entity.on_ground:
            entity.velocity_y = jump_velocity
            entity.on_ground = False
            return True
        return False
    
    def move_towards(self, entity, target_pos, speed):
        """Move entity towards a target position"""
        dx = target_pos[0] - entity.rect.centerx
        dy = target_pos[1] - entity.rect.centery
        distance = max(1, (dx**2 + dy**2)**0.5)
        
        # Normalize and apply speed
        entity.velocity_x = (dx / distance) * speed
        entity.velocity_y = (dy / distance) * speed
    
    def stop(self, entity):
        """Stop entity movement"""
        entity.velocity_x = 0
        entity.velocity_y = 0