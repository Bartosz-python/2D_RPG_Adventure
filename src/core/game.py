"""
src/core/game.py
Main game controller
"""
import pygame
from src.config.settings import *
from src.entities.player import Player
from src.managers.state_manager import StateManager
from src.managers.map_manager import MapManager
from src.managers.ui_manager import UIManager
from src.managers.quest_manager import QuestManager
from src.managers.day_night_manager import DayNightManager
from src.managers.asset_manager import AssetManager
from src.managers.enemy_spawn_manager import EnemySpawnManager

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        
        # Initialize managers
        self.asset_manager = AssetManager()
        self.state_manager = StateManager(STATE_TUTORIAL)
        self.map_manager = MapManager(self.asset_manager)
        self.day_night_manager = DayNightManager()
        self.quest_manager = QuestManager()
        self.ui_manager = UIManager(self.map_manager)
        self.enemy_spawn_manager = EnemySpawnManager()
        
        # Tutorial play button
        self.tutorial_play_button = None
        
        # Load initial map first
        self.current_map = self.map_manager.load_map(MAP_MAIN)
        
        # Initialize player (position on ground after map is loaded)
        # Ground is at y=25, player height is 2 tiles, so position at y=23
        # Start player at center of map
        start_x = (self.current_map.width * TILE_SIZE) // 2
        start_y = 23 * TILE_SIZE
        self.player = Player(start_x, start_y, self.asset_manager)
        
        # Track player spawn position for depth calculation
        self.player_spawn_y = start_y
        
        # Initialize enemy spawn configurations
        self._setup_enemy_spawns()
        
        # Start with tutorial (as per readme)
        # Player starts with club weapon until tutorial is complete
        
        # Camera offset
        self.camera_x = 0
        self.camera_y = 0
    
    def handle_event(self, event):
        """Handle pygame events"""
        current_state = self.state_manager.get_state()
        
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check tutorial Play button
                if current_state == STATE_TUTORIAL:
                    if self.tutorial_play_button and self.tutorial_play_button.collidepoint(event.pos):
                        self.state_manager.set_state(STATE_WEAPON_SELECTION)
                        return None
                
                # Check title bar buttons first
                title_bar_action = self.ui_manager.handle_title_bar_click(event.pos)
                if title_bar_action:
                    return title_bar_action  # Return action to main loop
                
                # Check exit button
                if hasattr(self.ui_manager, 'exit_button_rect') and self.ui_manager.exit_button_rect:
                    if self.ui_manager.exit_button_rect.collidepoint(event.pos):
                        self.running = False
                        return 'quit'
                
                # Check menu buttons
                if self.ui_manager.active_menu:
                    self.ui_manager.handle_menu_click(event.pos, self.player)
                    # Don't pass mouse click to player if menu is open
                    return
                
                # Handle block attack (only in gameplay, not in menus)
                current_state = self.state_manager.get_state()
                if current_state in [STATE_MAIN_MAP, STATE_EXPLORATION]:
                    # Try to attack block at mouse position (within 3-block radius)
                    self.player.attack_block(event.pos, self.camera_x, self.camera_y, self.current_map)
                    # Also trigger normal attack for enemies (handled in player.update)
                    self.player.keys['attack'] = True
        
        # Handle platform placement (Q key) in exploration map only
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            # Disable building completely on main map
            if current_state == STATE_MAIN_MAP:
                return None
            
            if current_state == STATE_EXPLORATION:
                # Get mouse position in world coordinates
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = mouse_x + self.camera_x
                world_y = mouse_y + self.camera_y
                
                # Check if within placement range (1.5x mining radius)
                player_center_x, player_center_y = self.player.rect.center
                distance = ((world_x - player_center_x)**2 + (world_y - player_center_y)**2)**0.5
                mining_radius = TILE_SIZE * 4.5  # Base mining radius
                placement_radius = mining_radius * 1.5  # 1.5x mining radius
                
                if distance <= placement_radius:
                    # Align to block grid (top line of block)
                    grid_x = world_x // TILE_SIZE
                    grid_y = world_y // TILE_SIZE
                    
                    # Disable building within 10 blocks of the top edge
                    if grid_y < 10:
                        return None
                    
                    # Check if player has dirt in inventory
                    if self.player.inventory.has_item('dirt', 1):
                        # Place platform and consume dirt
                        if self.current_map.add_platform(grid_x, grid_y):
                            self.player.inventory.remove_item('dirt', 1)
        
        # Handle ESC key based on context
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Close active menu if one is open
            if self.ui_manager.active_menu:
                self.ui_manager.close_menu()
            # Allow ESC to go back from weapon selection to tutorial
            elif current_state == STATE_WEAPON_SELECTION:
                self.state_manager.set_state(STATE_TUTORIAL)
            # Only quit if in gameplay or tutorial (and no menu open)
            elif current_state in [STATE_MAIN_MAP, STATE_EXPLORATION, STATE_TUTORIAL]:
                self.running = False
        
        # Handle state-specific events
        if event.type == pygame.KEYDOWN:
            if current_state == STATE_TUTORIAL:
                # Handle ENTER to progress from tutorial
                if event.key == pygame.K_RETURN:
                    self.state_manager.set_state(STATE_WEAPON_SELECTION)
                # Debug: Press P to skip directly to gameplay
                elif event.key == pygame.K_p:
                    self.player.equip_weapon('sword')
                    self.state_manager.set_state(STATE_MAIN_MAP)
                    # Position player at top edge of green block (center x, on ground level)
                    # Ground is at y=25, player height is 2 tiles, so position at y=23
                    self.player.rect.x = (self.current_map.width * TILE_SIZE) // 2
                    self.player.rect.y = 23 * TILE_SIZE  # Top edge of green block
                    # Reset velocity to prevent issues
                    self.player.velocity_x = 0
                    self.player.velocity_y = 0
                else:
                    self.quest_manager.handle_tutorial_input(event, self.player)
            elif current_state == STATE_WEAPON_SELECTION:
                self.handle_weapon_selection(event)
            elif current_state in [STATE_MAIN_MAP, STATE_EXPLORATION]:
                self.handle_interaction(event)
        
        # Always pass input events to player when in gameplay (both KEYDOWN and KEYUP)
        if current_state in [STATE_MAIN_MAP, STATE_EXPLORATION]:
            self.player.handle_input(event)
    
    def handle_weapon_selection(self, event):
        """Handle weapon selection after tutorial"""
        if event.key == pygame.K_1:
            self.player.equip_weapon('sword')
            self.state_manager.set_state(STATE_MAIN_MAP)
            # Position player at top edge of green block (center x, on ground level)
            # Ground is at y=25, player height is 2 tiles, so position at y=23
            self.player.rect.x = (self.current_map.width * TILE_SIZE) // 2
            self.player.rect.y = 23 * TILE_SIZE  # Top edge of green block
            # Reset velocity to prevent issues
            self.player.velocity_x = 0
            self.player.velocity_y = 0
        elif event.key == pygame.K_2:
            self.player.equip_weapon('wand')
            self.state_manager.set_state(STATE_MAIN_MAP)
            # Position player at top edge of green block (center x, on ground level)
            # Ground is at y=25, player height is 2 tiles, so position at y=23
            self.player.rect.x = (self.current_map.width * TILE_SIZE) // 2
            self.player.rect.y = 23 * TILE_SIZE  # Top edge of green block
            # Reset velocity to prevent issues
            self.player.velocity_x = 0
            self.player.velocity_y = 0
        elif event.key == pygame.K_3:
            self.player.equip_weapon('bow')
            self.state_manager.set_state(STATE_MAIN_MAP)
            # Position player at top edge of green block (center x, on ground level)
            # Ground is at y=25, player height is 2 tiles, so position at y=23
            self.player.rect.x = (self.current_map.width * TILE_SIZE) // 2
            self.player.rect.y = 23 * TILE_SIZE  # Top edge of green block
            # Reset velocity to prevent issues
            self.player.velocity_x = 0
            self.player.velocity_y = 0
    
    def handle_interaction(self, event):
        """Handle player interactions with environment"""
        if event.key == pygame.K_e:
            # Check for building interactions - check if player is near any building
            player_center = self.player.rect.center
            building = self.current_map.get_building_at(player_center)
            
            # Also check nearby buildings (within interaction range)
            if not building:
                for b in self.current_map.buildings:
                    if b.is_player_near(self.player.rect):
                        building = b
                        break
            
            if building:
                self.ui_manager.open_building_menu(building.building_type, self.player)
    
    def update(self, dt):
        """Update game state"""
        current_state = self.state_manager.get_state()
        
        # Update day/night cycle (only in exploration)
        if current_state == STATE_EXPLORATION:
            self.day_night_manager.update(dt)
            
            # Check for map reset every 7 days
            if self.day_night_manager.should_reset_map():
                self.current_map.reset_exploration()
        
        # Update tutorial quest
        if current_state == STATE_TUTORIAL:
            if self.quest_manager.update_tutorial(self.player, dt):
                self.state_manager.set_state(STATE_WEAPON_SELECTION)
        
        # Update player
        elif current_state in [STATE_MAIN_MAP, STATE_EXPLORATION]:
            # Disable movement if menu is open on main map
            menu_open = (current_state == STATE_MAIN_MAP and self.ui_manager.active_menu is not None)
            self.player.update(dt, self.current_map, menu_open=menu_open)
            
            # Update enemies
            self.current_map.update_enemies(dt, self.player)
            
            # Update enemy spawn system (only in exploration)
            if current_state == STATE_EXPLORATION:
                self.enemy_spawn_manager.update(
                    dt, 
                    self.current_map, 
                    self.day_night_manager,
                    self.player_spawn_y,
                    self.player.rect.centery
                )
            
            # Update camera
            self.update_camera()
            
            # Check for map transitions
            self.check_map_transitions()
    
    def _setup_enemy_spawns(self):
        """Setup enemy spawn configurations"""
        # Example configurations - can be customized
        # Goblin: spawns during day, at any depth
        self.enemy_spawn_manager.register_enemy_type(
            'goblin',
            {'day': True, 'night': False, 'min_depth': 0, 'max_depth': None},
            spawn_rate=0.15,
            spawn_interval=8.0,
            max_count=3
        )
        
        # Skeleton: spawns during night, at depth 5+
        self.enemy_spawn_manager.register_enemy_type(
            'skeleton',
            {'day': False, 'night': True, 'min_depth': 5, 'max_depth': None},
            spawn_rate=0.1,
            spawn_interval=10.0,
            max_count=2
        )
        
        # Orc: spawns during night, at depth 10+
        self.enemy_spawn_manager.register_enemy_type(
            'orc',
            {'day': False, 'night': True, 'min_depth': 10, 'max_depth': None},
            spawn_rate=0.05,
            spawn_interval=15.0,
            max_count=1
        )
    
    def get_depth_level(self):
        """Calculate current depth level (blocks below spawn)"""
        depth = max(0, int((self.player.rect.y - self.player_spawn_y) / TILE_SIZE))
        return depth
    
    def update_camera(self):
        """Center camera on player (only on exploration map)"""
        # Only follow player on exploration map
        if self.current_map.map_type == MAP_EXPLORATION:
            self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
            self.camera_y = self.player.rect.centery - SCREEN_HEIGHT // 2
            
            # Clamp camera to map bounds
            max_x = self.current_map.width * TILE_SIZE - SCREEN_WIDTH
            max_y = self.current_map.height * TILE_SIZE - SCREEN_HEIGHT
            
            self.camera_x = max(0, min(self.camera_x, max_x))
            self.camera_y = max(0, min(self.camera_y, max_y))
        else:
            # For other maps, keep original behavior (camera follows player)
            self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
            self.camera_y = self.player.rect.centery - SCREEN_HEIGHT // 2
            
            # Clamp camera to map bounds
            max_x = self.current_map.width * TILE_SIZE - SCREEN_WIDTH
            max_y = self.current_map.height * TILE_SIZE - SCREEN_HEIGHT
            
            self.camera_x = max(0, min(self.camera_x, max_x))
            self.camera_y = max(0, min(self.camera_y, max_y))
    
    def check_map_transitions(self):
        """Check if player is transitioning between maps"""
        exit_point = self.current_map.get_exit_at(self.player.rect.center)
        if exit_point:
            if exit_point == "exploration":
                self.current_map = self.map_manager.load_map(MAP_EXPLORATION)
                self.state_manager.set_state(STATE_EXPLORATION)
                # Position player on ground in exploration map
                # Ground is at y=35, player height is 2 tiles, so position at y=33
                self.player.rect.x = 100
                spawn_y = 33 * TILE_SIZE
                self.player.rect.y = spawn_y
                # Update spawn position for depth calculation
                self.player_spawn_y = spawn_y
                # Reset velocity to prevent issues
                self.player.velocity_x = 0
                self.player.velocity_y = 0
            elif exit_point == "main":
                self.current_map = self.map_manager.load_map(MAP_MAIN)
                self.state_manager.set_state(STATE_MAIN_MAP)
                # Position player on ground in main map (center)
                # Ground is at y=25, player height is 2 tiles, so position at y=23
                self.player.rect.x = (self.current_map.width * TILE_SIZE) // 2
                spawn_y = 23 * TILE_SIZE
                self.player.rect.y = spawn_y
                # Update spawn position for depth calculation
                self.player_spawn_y = spawn_y
                # Reset velocity to prevent issues
                self.player.velocity_x = 0
                self.player.velocity_y = 0
    
    def render(self, screen):
        """Render game"""
        screen.fill(BLACK)
        
        current_state = self.state_manager.get_state()
        
        # Render title bar first (always visible on top)
        self.ui_manager.render_title_bar(screen)
        
        # Render tutorial
        if current_state == STATE_TUTORIAL:
            self.render_tutorial(screen)
        
        # Render weapon selection
        elif current_state == STATE_WEAPON_SELECTION:
            self.render_weapon_selection(screen)
        
        # Render gameplay
        elif current_state in [STATE_MAIN_MAP, STATE_EXPLORATION]:
            # Apply day/night overlay
            if current_state == STATE_EXPLORATION:
                overlay_alpha = self.day_night_manager.get_overlay_alpha()
            else:
                overlay_alpha = 0
            
            # Render map (with day/night cycle for background)
            self.current_map.render(screen, self.camera_x, self.camera_y, self.day_night_manager)
            
            # Render mining radius indicator on exploration map
            if current_state == STATE_EXPLORATION:
                self.render_mining_radius(screen)
            
            # Render player
            self.player.render(screen, self.camera_x, self.camera_y)
            
            # Render "Interact" text if player is near a building (only on main map)
            if current_state == STATE_MAIN_MAP:
                self.render_interact_prompt(screen)
            
            # Apply day/night overlay
            if overlay_alpha > 0:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill((0, 0, 50))
                overlay.set_alpha(overlay_alpha)
                screen.blit(overlay, (0, 0))
            
            # Render UI (always on top)
            depth_level = self.get_depth_level() if current_state == STATE_EXPLORATION else 0
            self.ui_manager.render(screen, self.player, self.day_night_manager, depth_level, current_state)
    
    def render_mining_radius(self, screen):
        """Render semi-transparent gray circle showing mining radius on exploration map"""
        # Mining radius is 4.5 blocks (increased by 1.5x from 3)
        mining_radius = TILE_SIZE * 4.5
        
        # Get player center position in screen coordinates
        player_center_x = self.player.rect.centerx - self.camera_x
        player_center_y = self.player.rect.centery - self.camera_y
        
        # Create a surface for the circle with alpha
        radius_surface = pygame.Surface((mining_radius * 2, mining_radius * 2), pygame.SRCALPHA)
        
        # Draw semi-transparent gray circle (outline only)
        gray_color = (128, 128, 128, 100)  # Gray with alpha
        pygame.draw.circle(radius_surface, gray_color, (mining_radius, mining_radius), mining_radius, 2)
        
        # Blit the circle surface to screen
        screen.blit(radius_surface, (player_center_x - mining_radius, player_center_y - mining_radius))
    
    def render_interact_prompt(self, screen):
        """Render 'Interact' text above player when near a building"""
        # Check if player is near any building
        player_near_building = False
        for building in self.current_map.buildings:
            if building.is_player_near(self.player.rect):
                player_near_building = True
                break
        
        if player_near_building:
            # Calculate screen position for text (above player)
            player_screen_x = self.player.rect.centerx - self.camera_x
            player_screen_y = self.player.rect.top - self.camera_y - 20  # 20 pixels above player
            
            # Create small font for interact text
            small_font = pygame.font.Font(None, 24)
            interact_text = small_font.render("Interact", True, WHITE)
            
            # Draw background for text (semi-transparent)
            text_bg_rect = pygame.Rect(
                player_screen_x - interact_text.get_width() // 2 - 5,
                player_screen_y - 2,
                interact_text.get_width() + 10,
                interact_text.get_height() + 4
            )
            bg_surface = pygame.Surface((text_bg_rect.width, text_bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 150))  # Semi-transparent black
            screen.blit(bg_surface, text_bg_rect)
            
            # Draw text centered above player
            screen.blit(interact_text, (player_screen_x - interact_text.get_width() // 2, player_screen_y))
    
    def render_tutorial(self, screen):
        """Render tutorial screen"""
        # Background
        screen.fill((20, 20, 40))
        
        font = pygame.font.Font(None, 36)
        title = font.render("Welcome to Wild Eldoria!", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        instructions = [
            "Use W/A/S/D or Arrow Keys to move",
            "Press W or Up to jump",
            "Press E to interact with objects",
            "Press left mouse button to attack or destroy blocks",
            "Press ESC to quit",
            "",
            "Click the Play button below to continue to weapon selection",
            "Or complete your first quest to continue!"
        ]
        
        small_font = pygame.font.Font(None, 24)
        y = 200
        for instruction in instructions:
            text = small_font.render(instruction, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 30
        
        # Play button
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = y + 40
        play_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        self.tutorial_play_button = play_button_rect
        
        # Draw Play button
        pygame.draw.rect(screen, (80, 150, 80), play_button_rect)
        pygame.draw.rect(screen, (100, 200, 100), play_button_rect, 3)
        
        button_font = pygame.font.Font(None, 32)
        play_text = button_font.render("Play", True, WHITE)
        play_text_x = button_x + button_width // 2 - play_text.get_width() // 2
        play_text_y = button_y + button_height // 2 - play_text.get_height() // 2
        screen.blit(play_text, (play_text_x, play_text_y))
    
    def render_weapon_selection(self, screen):
        """Render weapon selection screen"""
        # Background
        screen.fill((20, 20, 40))
        
        font = pygame.font.Font(None, 36)
        title = font.render("Choose Your Weapon", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        weapons = [
            "1 - Sword (Balanced damage and speed)",
            "2 - Wand (Magic attacks, ranged)",
            "3 - Bow (High damage, slow)"
        ]
        
        small_font = pygame.font.Font(None, 28)
        y = 250
        for weapon in weapons:
            text = small_font.render(weapon, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 60
        
        # Add instruction
        esc_text = small_font.render("Press ESC to go back", True, LIGHT_GRAY)
        screen.blit(esc_text, (SCREEN_WIDTH // 2 - esc_text.get_width() // 2, y + 40))