"""
src/world/map.py
Map class containing blocks, enemies, buildings
"""
import pygame
from src.world.block import Block
from src.world.building import Building
from src.entities.enemy import Enemy
from src.config.settings import *

class Map:
    def __init__(self, width, height, asset_manager, map_type=None):
        self.width = width
        self.height = height
        self.asset_manager = asset_manager
        self.map_type = map_type  # Store map type for special rendering
        
        # Grid of blocks
        self.blocks = []
        self.buildings = []
        self.enemies = []
        self.exits = []
        
        # Coins/items on ground
        self.items = []
        
        # Load background images for main map
        self.background_image = None
        self.background_layer2 = None
        if self.map_type == MAP_MAIN:
            self.background_image = asset_manager.get_sprite('background_main')
            if self.background_image:
                # Scale background to screen size if needed
                bg_width, bg_height = self.background_image.get_size()
                if bg_width != SCREEN_WIDTH or bg_height != SCREEN_HEIGHT:
                    self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                # Convert to support alpha for transparency
                if not self.background_image.get_flags() & pygame.SRCALPHA:
                    self.background_image = self.background_image.convert_alpha()
            
            # Load additional background layer (foreground layer)
            self.background_layer2 = asset_manager.get_sprite('background_layer2')
            if self.background_layer2:
                # Scale to screen size if needed
                layer2_width, layer2_height = self.background_layer2.get_size()
                if layer2_width != SCREEN_WIDTH or layer2_height != SCREEN_HEIGHT:
                    self.background_layer2 = pygame.transform.scale(self.background_layer2, (SCREEN_WIDTH, SCREEN_HEIGHT))
                # Ensure it supports alpha (should already have it, but make sure)
                if not self.background_layer2.get_flags() & pygame.SRCALPHA:
                    self.background_layer2 = self.background_layer2.convert_alpha()
        
        # Add invisible collision blocks at map edges
        self._add_edge_collisions()
    
    def _add_edge_collisions(self):
        """Add invisible collision blocks at map edges"""
        # Use grid coordinates (Block multiplies by TILE_SIZE internally)
        wall_thickness = 2  # 2 tiles thick walls to prevent clipping
        
        # Left wall (negative x coordinates)
        for y in range(self.height):
            for wx in range(-wall_thickness, 0):
                block = Block(wx, y, 'stone', self.asset_manager, destructible=False)
                self.blocks.append(block)
        
        # Right wall (beyond map width)
        for y in range(self.height):
            for wx in range(self.width, self.width + wall_thickness):
                block = Block(wx, y, 'stone', self.asset_manager, destructible=False)
                self.blocks.append(block)
        
        # Top wall (negative y coordinates)
        for x in range(-wall_thickness, self.width + wall_thickness):
            for wy in range(-wall_thickness, 0):
                block = Block(x, wy, 'stone', self.asset_manager, destructible=False)
                self.blocks.append(block)
        
        # Bottom wall (beyond map height)
        for x in range(-wall_thickness, self.width + wall_thickness):
            for wy in range(self.height, self.height + wall_thickness):
                block = Block(x, wy, 'stone', self.asset_manager, destructible=False)
                self.blocks.append(block)
    
    def add_block(self, x, y, block_type, destructible=True):
        """Add block to map"""
        block = Block(x, y, block_type, self.asset_manager, destructible)
        self.blocks.append(block)
    
    def add_platform(self, x, y):
        """Add one-way platform at grid coordinates"""
        # Check if spot is empty (no blocks at this position)
        if self.is_spot_empty(x * TILE_SIZE, y * TILE_SIZE):
            platform = Block(x, y, 'stone', self.asset_manager, destructible=False, is_platform=True)
            self.blocks.append(platform)
            return True
        return False
    
    def is_spot_empty(self, world_x, world_y):
        """Check if a world coordinate position is empty (no blocks)"""
        # Check a small area around the position (platform width and a bit of height)
        # Platform is TILE_SIZE * 2 wide and 4 pixels tall
        check_rect = pygame.Rect(world_x, world_y, TILE_SIZE * 2, TILE_SIZE)
        for block in self.blocks:
            # Skip platforms when checking (allow placing platforms near other platforms)
            if block.is_platform:
                continue
            if block.rect.colliderect(check_rect):
                return False
        return True
    
    def remove_block(self, block):
        """Remove block from map"""
        if block in self.blocks:
            self.blocks.remove(block)
    
    def get_block_at(self, x, y):
        """Get block at world coordinates"""
        for block in self.blocks:
            if block.rect.collidepoint(x, y):
                return block
        return None
    
    def get_colliding_blocks(self, rect):
        """Get all blocks colliding with rect"""
        return [block for block in self.blocks if block.rect.colliderect(rect)]
    
    def add_building(self, x, y, building_type):
        """Add building to map"""
        building = Building(x, y, building_type, self.asset_manager)
        self.buildings.append(building)
    
    def get_building_at(self, pos):
        """Get building at position"""
        for building in self.buildings:
            if building.rect.collidepoint(pos):
                return building
        return None
    
    def add_exit(self, x, y, destination):
        """Add exit point"""
        exit_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE * 2, TILE_SIZE * 2)
        self.exits.append({'rect': exit_rect, 'destination': destination})
    
    def get_exit_at(self, pos):
        """Get exit at position"""
        for exit_point in self.exits:
            if exit_point['rect'].collidepoint(pos):
                return exit_point['destination']
        return None
    
    def spawn_enemy(self, x, y, enemy_type, sprite_path=None):
        """Spawn enemy on map
        Args:
            x, y: Grid coordinates
            enemy_type: Type of enemy
            sprite_path: Optional custom sprite path for enemy graphics
        """
        enemy = Enemy(x * TILE_SIZE, y * TILE_SIZE, enemy_type, self.asset_manager, sprite_path)
        self.enemies.append(enemy)
    
    def update_enemies(self, dt, player):
        """Update all enemies"""
        for enemy in self.enemies[:]:
            enemy.update(dt, player, self)
            
            # Remove dead enemies
            if enemy.hp <= 0:
                self.enemies.remove(enemy)
    
    def reset_exploration(self):
        """Reset exploration map (regenerate blocks and enemies)"""
        # This would regenerate the map
        pass
    
    def render(self, screen, camera_x, camera_y, day_night_manager=None, render_buildings=True, exclude_buildings=None):
        """Render entire map"""
        if exclude_buildings is None:
            exclude_buildings = []
        # Calculate day/night darkness factor (0.0 = full day, 1.0 = full night)
        # Transition starts from day (0.5) to night (0.75), then full night
        darkness_factor = 0.0
        if day_night_manager:
            time_of_day = day_night_manager.get_time_of_day()
            # Start transition from day to night (0.5 to 0.75)
            if 0.5 <= time_of_day < 0.75:
                # Transition from day to night: 0.0 to 0.7 (not fully dark to keep visibility)
                darkness_factor = ((time_of_day - 0.5) / 0.25) * 0.7
            elif time_of_day >= 0.75 or time_of_day < 0.25:
                # Night: 0.7 darkness (not fully dark)
                darkness_factor = 0.7
            elif 0.25 <= time_of_day < 0.5:
                # Dawn: transition from night to day
                darkness_factor = 0.7 * (1 - (time_of_day - 0.25) / 0.25)
        
        # Base colors (day)
        bg_color_top_day = (135, 206, 250)  # Light sky blue
        bg_color_mid_day = (176, 196, 222)  # Light steel blue
        bg_color_bottom_day = (230, 230, 250)  # Lavender
        
        # Night colors (darker but still visible)
        bg_color_top_night = (20, 20, 40)  # Dark blue
        bg_color_mid_night = (15, 15, 30)  # Darker blue
        bg_color_bottom_night = (10, 10, 20)  # Very dark blue
        
        # Interpolate between day and night colors
        bg_color_top = tuple(int(bg_color_top_day[i] * (1 - darkness_factor) + bg_color_top_night[i] * darkness_factor) for i in range(3))
        bg_color_mid = tuple(int(bg_color_mid_day[i] * (1 - darkness_factor) + bg_color_mid_night[i] * darkness_factor) for i in range(3))
        bg_color_bottom = tuple(int(bg_color_bottom_day[i] * (1 - darkness_factor) + bg_color_bottom_night[i] * darkness_factor) for i in range(3))
        
        # Render background
        if self.map_type == MAP_MAIN and self.background_image:
            # Calculate alpha for first background based on day/night cycle
            # Day: alpha = 200 (semi-transparent, brighter)
            # Night: alpha = 100 (more transparent, dimmer)
            # Transition smoothly between day and night
            base_alpha_day = 200
            base_alpha_night = 100
            current_alpha = int(base_alpha_day * (1 - darkness_factor) + base_alpha_night * darkness_factor)
            
            # Render first background with alpha (semi-transparent)
            bg1_surface = self.background_image.copy()
            bg1_surface.set_alpha(current_alpha)
            screen.blit(bg1_surface, (0, 0))
            
            # Render additional background layer (in front of first background) - no dimming or transparency
            if self.background_layer2:
                screen.blit(self.background_layer2, (0, 0))
        else:
            # Render background (sky gradient) - regenerate each frame to reflect day/night changes
            self._bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                if ratio < 0.5:
                    # Top half: top to mid
                    local_ratio = ratio * 2
                    r = int(bg_color_top[0] * (1 - local_ratio) + bg_color_mid[0] * local_ratio)
                    g = int(bg_color_top[1] * (1 - local_ratio) + bg_color_mid[1] * local_ratio)
                    b = int(bg_color_top[2] * (1 - local_ratio) + bg_color_mid[2] * local_ratio)
                else:
                    # Bottom half: mid to bottom
                    local_ratio = (ratio - 0.5) * 2
                    r = int(bg_color_mid[0] * (1 - local_ratio) + bg_color_bottom[0] * local_ratio)
                    g = int(bg_color_mid[1] * (1 - local_ratio) + bg_color_bottom[1] * local_ratio)
                    b = int(bg_color_mid[2] * (1 - local_ratio) + bg_color_bottom[2] * local_ratio)
                pygame.draw.line(self._bg_surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            screen.blit(self._bg_surface, (0, 0))
        
        # Render blocks for exploration map
        if self.map_type != MAP_MAIN:
            # Render blocks normally for other maps
            for block in self.blocks:
                block.render(screen, camera_x, camera_y)
        
        # Render buildings (excluding specified ones if needed)
        if render_buildings:
            for building in self.buildings:
                if building.building_type not in exclude_buildings:
                    building.render(screen, camera_x, camera_y)
        
        # Render exits (visual indicator with glow effect)
        for exit_point in self.exits:
            screen_x = exit_point['rect'].x - camera_x
            screen_y = exit_point['rect'].y - camera_y
            
            # Glow effect
            glow_surface = pygame.Surface((exit_point['rect'].width + 8, exit_point['rect'].height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 255, 0, 100), 
                           (0, 0, exit_point['rect'].width + 8, exit_point['rect'].height + 8), 0)
            screen.blit(glow_surface, (screen_x - 4, screen_y - 4))
            
            # Main exit indicator
            exit_rect = pygame.Rect(screen_x, screen_y, exit_point['rect'].width, exit_point['rect'].height)
            pygame.draw.rect(screen, (255, 215, 0), exit_rect)  # Gold color
            pygame.draw.rect(screen, (255, 255, 100), exit_rect, 3)
            
            # Arrow indicator
            center_x = screen_x + exit_point['rect'].width // 2
            center_y = screen_y + exit_point['rect'].height // 2
            pygame.draw.polygon(screen, (255, 255, 255), [
                (center_x, center_y - 8),
                (center_x - 6, center_y),
                (center_x + 6, center_y)
            ])
        
        # Render enemies
        for enemy in self.enemies:
            enemy.render(screen, camera_x, camera_y)