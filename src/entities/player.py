"""
src/entities/player.py
Player character with movement, combat, and inventory
"""
import pygame
from src.config.settings import *
from src.systems.inventory import Inventory
from src.systems.equipment import Equipment

class Player:
    def __init__(self, x, y, asset_manager):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE * 2)
        self.asset_manager = asset_manager
        
        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = True  # Start on ground
        self.facing_right = True
        
        # Stats
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.gold = 0
        
        # Combat
        self.weapon = 'club'
        self.weapon_damage = CLUB_DAMAGE
        self.attack_cooldown = 0
        self.is_attacking = False
        
        # Systems
        self.inventory = Inventory(TOTAL_SLOTS)
        self.equipment = Equipment()
        
        # Block interaction
        self.destroying_block = None
        self.destroy_progress = 0
        
        # Input state
        self.keys = {
            'left': False,
            'right': False,
            'jump': False,
            'attack': False
        }
    
    def handle_input(self, event):
        """Handle keyboard input"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_a, pygame.K_LEFT]:
                self.keys['left'] = True
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                self.keys['right'] = True
            elif event.key in [pygame.K_w, pygame.K_UP]:
                self.keys['jump'] = True
            elif event.key == pygame.K_SPACE:
                self.keys['attack'] = True
        
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_a, pygame.K_LEFT]:
                self.keys['left'] = False
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                self.keys['right'] = False
            elif event.key in [pygame.K_w, pygame.K_UP]:
                self.keys['jump'] = False
            elif event.key == pygame.K_SPACE:
                self.keys['attack'] = False
    
    def update(self, dt, current_map):
        """Update player state"""
        # Get current key states for continuous movement
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        self.velocity_x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT] or self.keys['left']:
            self.velocity_x = -PLAYER_SPEED
            self.facing_right = False
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT] or self.keys['right']:
            self.velocity_x = PLAYER_SPEED
            self.facing_right = True
        
        # Apply horizontal movement
        self.rect.x += self.velocity_x * dt
        self.handle_collision(current_map, 'x')
        
        # Jumping (only use event-based, not continuous key check)
        if self.keys['jump'] and self.on_ground:
            self.velocity_y = PLAYER_JUMP_VELOCITY
            self.on_ground = False
            self.keys['jump'] = False  # Reset jump key to prevent continuous jumping
        
        # Apply gravity
        self.velocity_y += GRAVITY * dt
        self.velocity_y = min(self.velocity_y, 1000)  # Terminal velocity
        
        # Apply vertical movement
        self.rect.y += self.velocity_y * dt
        self.on_ground = False
        self.handle_collision(current_map, 'y')
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Handle attack (check both event-based and current key state)
        if (keys[pygame.K_SPACE] or self.keys['attack']) and self.attack_cooldown <= 0:
            self.perform_attack(current_map)
            self.attack_cooldown = ATTACK_COOLDOWN
            self.keys['attack'] = False  # Reset attack key
        
        # Update block destruction
        if self.destroying_block:
            self.destroy_progress += dt
            if self.destroy_progress >= BLOCK_DESTROY_TIME:
                self.finish_destroying_block(current_map)
    
    def handle_collision(self, current_map, axis):
        """Handle collision with map blocks and screen boundaries"""
        # Check left screen boundary (prevent player from leaving left side)
        if axis == 'x' and self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x = 0
            return
        
        collided_blocks = current_map.get_colliding_blocks(self.rect)
        
        if not collided_blocks:
            return
        
        for block in collided_blocks:
            if axis == 'x':
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = block.rect.left
                    self.velocity_x = 0
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
    
    def perform_attack(self, current_map):
        """Execute attack"""
        self.is_attacking = True
        
        # Create attack hitbox in front of player
        attack_range = TILE_SIZE * 1.5
        if self.facing_right:
            attack_rect = pygame.Rect(
                self.rect.right, 
                self.rect.top, 
                attack_range, 
                self.rect.height
            )
        else:
            attack_rect = pygame.Rect(
                self.rect.left - attack_range, 
                self.rect.top, 
                attack_range, 
                self.rect.height
            )
        
        # Check for enemy hits
        for enemy in current_map.enemies:
            if attack_rect.colliderect(enemy.rect):
                enemy.take_damage(self.weapon_damage)
                if enemy.hp <= 0:
                    self.gold += enemy.coin_value
                    current_map.enemies.remove(enemy)
    
    def start_destroying_block(self, current_map):
        """Start destroying a block"""
        # Find block in front of player
        check_x = self.rect.right if self.facing_right else self.rect.left - TILE_SIZE
        check_y = self.rect.centery
        
        block = current_map.get_block_at(check_x, check_y)
        if block and block.destructible:
            self.destroying_block = block
            self.destroy_progress = 0
    
    def finish_destroying_block(self, current_map):
        """Complete block destruction and add to inventory"""
        if self.destroying_block:
            # Random chance to get gold from blocks (10% chance)
            import random
            if random.random() < 0.1:
                gold_amount = random.randint(1, 5)
                self.add_gold(gold_amount)
            
            # Add block to inventory
            if self.inventory.add_item(self.destroying_block.block_type):
                current_map.remove_block(self.destroying_block)
            else:
                # Inventory full message handled by UI
                pass
            
            self.destroying_block = None
            self.destroy_progress = 0
    
    def equip_weapon(self, weapon_type):
        """Equip a weapon"""
        self.weapon = weapon_type
        
        if weapon_type == 'sword':
            self.weapon_damage = SWORD_DAMAGE
        elif weapon_type == 'wand':
            self.weapon_damage = WAND_DAMAGE
        elif weapon_type == 'bow':
            self.weapon_damage = BOW_DAMAGE
        elif weapon_type == 'club':
            self.weapon_damage = CLUB_DAMAGE
        
        self.equipment.equip('weapon', weapon_type)
    
    def take_damage(self, damage):
        """Take damage from enemy"""
        armor_reduction = self.equipment.get_total_armor()
        actual_damage = max(1, damage - armor_reduction)
        self.hp = max(0, self.hp - actual_damage)
    
    def heal(self, amount):
        """Heal player"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def add_gold(self, amount):
        """Add gold to player"""
        self.gold += amount
    
    def spend_gold(self, amount):
        """Spend gold, return True if successful"""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    def render(self, screen, camera_x, camera_y):
        """Render player"""
        # Calculate screen position
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Draw shadow first
        shadow_rect = pygame.Rect(screen_x + 2, screen_y + self.rect.height - 4, self.rect.width - 4, 4)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 100))
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw player body with gradient effect
        if self.is_attacking:
            # Attack color - bright orange/red
            base_color = (255, 100, 50)
            highlight_color = (255, 200, 100)
        else:
            # Normal color - nice blue/cyan
            base_color = (70, 130, 180)  # Steel blue
            highlight_color = (135, 206, 250)  # Light sky blue
        
        # Main body
        player_rect = pygame.Rect(screen_x, screen_y, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, base_color, player_rect)
        
        # Highlight on top
        highlight_rect = pygame.Rect(screen_x, screen_y, self.rect.width, self.rect.height // 3)
        pygame.draw.rect(screen, highlight_color, highlight_rect)
        
        # Border
        pygame.draw.rect(screen, (30, 30, 30), player_rect, 2)
        
        # Draw eyes
        eye_y = screen_y + self.rect.height // 3
        if self.facing_right:
            pygame.draw.circle(screen, WHITE, (screen_x + self.rect.width // 3, eye_y), 4)
            pygame.draw.circle(screen, BLACK, (screen_x + self.rect.width // 3 + 1, eye_y), 2)
        else:
            pygame.draw.circle(screen, WHITE, (screen_x + 2 * self.rect.width // 3, eye_y), 4)
            pygame.draw.circle(screen, BLACK, (screen_x + 2 * self.rect.width // 3 - 1, eye_y), 2)
        
        self.is_attacking = False