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
        # Pass screen dimensions to UI manager
        screen_width, screen_height = screen.get_size()
        # Check if in fullscreen mode (pygame doesn't have direct check, so we'll pass False initially)
        self.ui_manager = UIManager(self.map_manager, screen_width, screen_height, is_fullscreen=False)
        
        # Load initial map first
        self.current_map = self.map_manager.load_map(MAP_MAIN)
        
        # Initialize player (position on ground after map is loaded)
        # Ground is at y=25, player height is 1 tile, so position at y=24
        # Start player at center of map
        start_x = (self.current_map.width * TILE_SIZE) // 2
        start_y = 24 * TILE_SIZE
        self.player = Player(start_x, start_y, self.asset_manager)
        
        # Start with tutorial (as per readme)
        # Player starts with club weapon until tutorial is complete
        
        # Camera offset
        self.camera_x = 0
        self.camera_y = 0
    
    def update_screen_size(self, width, height, is_fullscreen=False):
        """Update screen size for UI and other components"""
        self.ui_manager.update_screen_size(width, height, is_fullscreen)
    
    def handle_event(self, event):
        """Handle pygame events"""
        current_state = self.state_manager.get_state()
        
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check menu buttons first (menu has overlay, so it should be checked first)
                if self.ui_manager.active_menu:
                    menu_handled = self.ui_manager.handle_menu_click(event.pos, self.player)
                    if menu_handled:
                        return  # Menu handled the click, don't process other buttons
                
        
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
                    # Ground is at y=25, player height is 1 tile, so position at y=24
                    self.player.rect.x = (self.current_map.width * TILE_SIZE) // 2
                    self.player.rect.y = 24 * TILE_SIZE  # Top edge of green block
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
        # But block input if menu is open
        if current_state in [STATE_MAIN_MAP, STATE_EXPLORATION]:
            if not self.ui_manager.active_menu:
                self.player.handle_input(event)
    
    def handle_weapon_selection(self, event):
        """Handle weapon selection after tutorial"""
        if event.key == pygame.K_1:
            self.player.equip_weapon('sword')
            self.state_manager.set_state(STATE_MAIN_MAP)
            # Position player at top edge of green block (center x, on ground level)
            # Ground is at y=25, player height is 1 tile, so position at y=24
            self.player.rect.x = (self.current_map.width * TILE_SIZE) // 2
            self.player.rect.y = 24 * TILE_SIZE  # Top edge of green block
            # Reset velocity to prevent issues
            self.player.velocity_x = 0
            self.player.velocity_y = 0
        elif event.key == pygame.K_2:
            self.player.equip_weapon('wand')
            self.state_manager.set_state(STATE_MAIN_MAP)
            # Position player at top edge of green block (center x, on ground level)
            # Ground is at y=25, player height is 1 tile, so position at y=24
            self.player.rect.x = (self.current_map.width * TILE_SIZE) // 2
            self.player.rect.y = 24 * TILE_SIZE  # Top edge of green block
            # Reset velocity to prevent issues
            self.player.velocity_x = 0
            self.player.velocity_y = 0
        elif event.key == pygame.K_3:
            self.player.equip_weapon('bow')
            self.state_manager.set_state(STATE_MAIN_MAP)
            # Position player at top edge of green block (center x, on ground level)
            # Ground is at y=25, player height is 1 tile, so position at y=24
            self.player.rect.x = (self.current_map.width * TILE_SIZE) // 2
            self.player.rect.y = 24 * TILE_SIZE  # Top edge of green block
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
            # Block player movement if menu is open
            if not self.ui_manager.active_menu:
                self.player.update(dt, self.current_map)
                
                # Update enemies
                self.current_map.update_enemies(dt, self.player)
                
                # Update camera
                self.update_camera()
                
                # Check for map transitions
                self.check_map_transitions()
            else:
                # Menu is open - stop player movement but still apply gravity
                # Reset horizontal velocity to stop movement
                self.player.velocity_x = 0
                # Still apply gravity so player doesn't float
                self.player.velocity_y += GRAVITY * dt
                self.player.velocity_y = min(self.player.velocity_y, 1000)
                # Apply vertical movement for gravity
                self.player.rect.y += self.player.velocity_y * dt
                self.player.on_ground = False
                self.player.handle_collision(self.current_map, 'y')
    
    def update_camera(self):
        """Center camera on player"""
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
                # Ground is at y=35, player height is 1 tile, so position at y=34
                self.player.rect.x = 100
                self.player.rect.y = 34 * TILE_SIZE
                # Reset velocity to prevent issues
                self.player.velocity_x = 0
                self.player.velocity_y = 0
            elif exit_point == "main":
                self.current_map = self.map_manager.load_map(MAP_MAIN)
                self.state_manager.set_state(STATE_MAIN_MAP)
                # Position player on ground in main map (center)
                # Ground is at y=25, player height is 1 tile, so position at y=24
                self.player.rect.x = (self.current_map.width * TILE_SIZE) // 2
                self.player.rect.y = 24 * TILE_SIZE
                # Reset velocity to prevent issues
                self.player.velocity_x = 0
                self.player.velocity_y = 0
    
    def render(self, screen):
        """Render game"""
        screen.fill(BLACK)
        
        current_state = self.state_manager.get_state()
        
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
            
            # Render map background and blocks (with day/night cycle for background)
            self.current_map.render(screen, self.camera_x, self.camera_y, self.day_night_manager)
            
            # Render buildings (before player, so player appears on top)
            for building in self.current_map.buildings:
                building.render(screen, self.camera_x, self.camera_y)
            
            # Render enemies (before player, so player appears on top)
            for enemy in self.current_map.enemies:
                enemy.render(screen, self.camera_x, self.camera_y)
            
            # Render player (on first plan - after buildings and enemies)
            self.player.render(screen, self.camera_x, self.camera_y)
            
            # Apply day/night overlay
            if overlay_alpha > 0:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill((0, 0, 50))
                overlay.set_alpha(overlay_alpha)
                screen.blit(overlay, (0, 0))
            
            # Render UI (always on top)
            self.ui_manager.render(screen, self.player, self.day_night_manager)
    
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
            "Press SPACE to attack or destroy blocks",
            "Press ESC to quit",
            "",
            "Press ENTER to continue to weapon selection",
            "Or complete your first quest to continue!"
        ]
        
        small_font = pygame.font.Font(None, 24)
        y = 200
        for instruction in instructions:
            text = small_font.render(instruction, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 30
    
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