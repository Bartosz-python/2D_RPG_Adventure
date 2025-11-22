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
        """Handle keyboard and mouse input"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_a, pygame.K_LEFT]:
                self.keys['left'] = True
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                self.keys['right'] = True
            elif event.key in [pygame.K_w, pygame.K_UP]:
                self.keys['jump'] = True
        
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_a, pygame.K_LEFT]:
                self.keys['left'] = False
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                self.keys['right'] = False
            elif event.key in [pygame.K_w, pygame.K_UP]:
                self.keys['jump'] = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                self.keys['attack'] = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.keys['attack'] = False
    
    def update(self, dt, current_map, menu_open=False):
        """Update player state"""
        # Get current key states for continuous movement
        keys = pygame.key.get_pressed()
        
        # Horizontal movement (disabled if menu is open)
        self.velocity_x = 0
        if not menu_open:
            if keys[pygame.K_a] or keys[pygame.K_LEFT] or self.keys['left']:
                self.velocity_x = -PLAYER_SPEED
                self.facing_right = False
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT] or self.keys['right']:
                self.velocity_x = PLAYER_SPEED
                self.facing_right = True
        
        # Apply horizontal movement
        self.rect.x += self.velocity_x * dt
        self.handle_collision(current_map, 'x')
        
        # Jumping (only use event-based, not continuous key check, disabled if menu is open)
        if not menu_open and self.keys['jump'] and self.on_ground:
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
        
        # Handle attack (only on click event, not while held)
        if self.keys['attack'] and self.attack_cooldown <= 0:
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
        
        # Check if S key is held (for falling through platforms)
        keys = pygame.key.get_pressed()
        holding_s = keys[pygame.K_s] or keys[pygame.K_DOWN]
        
        for block in collided_blocks:
            # Handle one-way platforms
            if block.is_platform:
                if axis == 'x':
                    # Platforms don't block horizontal movement
                    continue
                elif axis == 'y':
                    # Platforms only block from above
                    if self.velocity_y > 0:  # Falling
                        # Allow falling through if S is held
                        if holding_s:
                            continue
                        # Block from above - align player bottom to platform top
                        self.rect.bottom = block.rect.top
                        self.velocity_y = 0
                        self.on_ground = True
                    elif self.velocity_y < 0:  # Jumping up
                        # Allow passing through from below
                        continue
                continue
            
            # Regular block collision
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
        
        # Create attack hitbox in front of player (for enemies)
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
        
        # Block destruction is handled separately via attack_block method with mouse targeting
    
    def attack_block(self, mouse_pos, camera_x, camera_y, current_map):
        """Attack the top-left block of a 2x2 area at mouse position within a 4.5-block radius"""
        # Convert screen coordinates to world coordinates
        world_x = mouse_pos[0] + camera_x
        world_y = mouse_pos[1] + camera_y
        
        # Check if the targeted block is within a 4.5-block radius of the player (increased by 1.5x)
        player_center_x, player_center_y = self.rect.center
        distance = ((world_x - player_center_x)**2 + (world_y - player_center_y)**2)**0.5
        mining_radius = TILE_SIZE * 4.5  # 4.5-block radius (was 3, increased by 1.5x)
        if distance > mining_radius:
            return False
        
        # Find the top-left block of the 2x2 grid area containing the mouse position
        # Blocks are in a 2x2 grid, so find which 2x2 cell the mouse is in
        BLOCK_GRID_SIZE = TILE_SIZE * 2  # 2x2 block grid size
        grid_x = (world_x // BLOCK_GRID_SIZE) * BLOCK_GRID_SIZE
        grid_y = (world_y // BLOCK_GRID_SIZE) * BLOCK_GRID_SIZE
        
        # Find the top-left block at this grid position
        block = current_map.get_block_at(grid_x, grid_y)
        if block:
            # Handle platform destruction
            if block.is_platform:
                # Platforms are destroyed instantly
                current_map.remove_block(block)
                return True
            
            # Handle regular destructible blocks
            if block.destructible:
                # Apply damage to the block
                BLOCK_BASE_DAMAGE = 8
                damage = BLOCK_BASE_DAMAGE
                if block.take_damage(damage):
                    # Block destroyed
                    import random
                    # Random chance to get gold from blocks (10% chance)
                    if random.random() < 0.1:
                        gold_amount = random.randint(1, 5)
                        self.add_gold(gold_amount)
                    
                    # Add block to inventory and remove from map
                    if self.inventory.add_item(block.block_type):
                        current_map.remove_block(block)
                    return True
                return True  # Block damaged but not destroyed
        return False
    
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