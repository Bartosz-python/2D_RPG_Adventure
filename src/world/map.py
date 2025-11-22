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
    
    def render(self, screen, camera_x, camera_y, day_night_manager=None):
        """Render entire map"""
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
        
        # Special rendering for main map: green ground block
        if self.map_type == MAP_MAIN:
            # Calculate ground position (where blocks start)
            ground_y = 25 * TILE_SIZE  # Top of ground blocks
            ground_screen_y = ground_y - camera_y
            
            # Draw green ground block from ground_y to bottom of screen, full width
            # Always draw from top of screen if ground is above screen
            green_start_y = max(0, ground_screen_y)
            green_height = SCREEN_HEIGHT - green_start_y
            
            if green_height > 0:
                # Green color with gradient for depth
                green_base = (34, 139, 34)  # Forest green
                green_dark = (0, 100, 0)     # Dark green
                green_light = (50, 205, 50)  # Light green
                
                # Draw gradient green block (dociągnięty do rogów i dołu)
                for y_offset in range(green_height):
                    ratio = y_offset / max(green_height, 1)
                    # Gradient from light at top to dark at bottom
                    r = int(green_light[0] * (1 - ratio * 0.3) + green_base[0] * (ratio * 0.3))
                    g = int(green_light[1] * (1 - ratio * 0.3) + green_base[1] * (ratio * 0.3))
                    b = int(green_light[2] * (1 - ratio * 0.3) + green_base[2] * (ratio * 0.3))
                    pygame.draw.line(screen, (r, g, b), 
                                    (0, green_start_y + y_offset), 
                                    (SCREEN_WIDTH, green_start_y + y_offset))
                
                # Add texture lines for grass effect at top
                if ground_screen_y >= 0:
                    for i in range(0, SCREEN_WIDTH, 20):
                        pygame.draw.line(screen, green_dark, (i, ground_screen_y), (i, ground_screen_y + 5), 1)
                    
                    # Top border (grass line)
                    pygame.draw.line(screen, green_light, (0, ground_screen_y), (SCREEN_WIDTH, ground_screen_y), 3)
        else:
            # Render blocks normally for other maps
            for block in self.blocks:
                block.render(screen, camera_x, camera_y)
        
        # Render buildings
        for building in self.buildings:
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