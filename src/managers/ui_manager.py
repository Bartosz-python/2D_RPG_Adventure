"""
src/managers/ui_manager.py
UI rendering and interaction management
"""
import pygame
from src.config.settings import *

class UIManager:
    def __init__(self, map_manager):
        # Accept map_manager but also need asset_manager for compatibility
        self.map_manager = map_manager
        self.asset_manager = map_manager.asset_manager if hasattr(map_manager, 'asset_manager') else None
        self.active_menu = None
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Track building upgrade levels (0 = no upgrades, 1 = first upgrade, 2 = second upgrade)
        self.building_upgrades = {
            BUILDING_SMITH: 0,
            BUILDING_TAILOR: 0,
            BUILDING_WITCH: 0,
            BUILDING_FIREPLACE: 0,
            BUILDING_BEDROOM: 0
        }
        
        # Slot size (define first, used in position calculations)
        self.slot_size = 50
        self.slot_padding = 5
        
        # UI element positions (centered and fully visible with padding)
        padding = 70  # Safe padding from screen edges (for other elements)
        
        # Top-left corner: Inventory (10 pixels from left and top)
        inventory_bar_width = (self.slot_size + self.slot_padding) * VISIBLE_SLOTS - self.slot_padding
        inventory_x = 25  # 10 pixels from left border
        inventory_y = 10  # 10 pixels from top border
        self.inventory_pos = (inventory_x, inventory_y)
        
        # HP bar below inventory (centered with inventory)
        hp_bar_width = 350
        hp_bar_x = inventory_x + (inventory_bar_width - hp_bar_width) // 2
        self.hp_bar_pos = (hp_bar_x, inventory_y + 90)  # Below inventory
        
        # Top-right corner: Exit button
        exit_btn_size = 40
        self.exit_button_pos = (SCREEN_WIDTH - exit_btn_size - padding, padding)
        self.exit_button_rect = None
        
        # Top-right corner: Day counter and depth (30 pixels from right, same height as inventory)
        day_counter_width = 150
        # Position will be calculated in render to align right edge 30px from screen edge
        self.day_counter_pos = (SCREEN_WIDTH - 30, inventory_y)  # Same y as inventory
        
        # Bottom-center: Stats and Equipment (centered, 10 pixels from bottom)
        equipment_bar_width = (self.slot_size + self.slot_padding) * 7 - self.slot_padding
        equipment_x = SCREEN_WIDTH // 2 - equipment_bar_width // 2
        bottom_margin = 10  # 10 pixels from bottom edge
        self.equipment_pos = (equipment_x, SCREEN_HEIGHT - bottom_margin - self.slot_size - 30)
        
        # Stats above equipment bar (centered)
        stats_width = 500
        stats_x = SCREEN_WIDTH // 2 - stats_width // 2
        self.stats_pos = (stats_x, SCREEN_HEIGHT - bottom_margin - self.slot_size - 75)
        
        # Title bar settings
        self.title_bar_height = 35
        self.title_bar_button_size = 30
        self.title_bar_button_padding = 5
        self.title_bar_buttons = {}  # Will store button rects
    
    def render(self, screen, player, day_night_manager, depth_level=0, current_state=None, timer_remaining=0):
        """Render all UI elements"""
        # Note: Title bar is rendered separately in game.render() to be always visible
        self.render_inventory(screen, player)
        self.render_hp_bar(screen, player)  # Gold is now in HP bar
        self.render_equipment(screen, player)
        self.render_stats(screen, player)
        self.render_day_counter(screen, day_night_manager)
        self.render_depth_level(screen, depth_level)
        
        # Render exploration timer (only on exploration map)
        from src.config.settings import STATE_EXPLORATION
        if current_state == STATE_EXPLORATION and timer_remaining > 0:
            self.render_exploration_timer(screen, timer_remaining)
        
        # Render platform placement text on exploration map
        if current_state == STATE_EXPLORATION:
            self.render_platform_text(screen)
        
        # Render active menu if any
        if self.active_menu:
            self.render_menu(screen, player)
    
    def render_inventory(self, screen, player):
        """Render visible inventory slots (centered)"""
        x, y = self.inventory_pos
        
        # Calculate centered position for slots
        inventory_bar_width = (self.slot_size + self.slot_padding) * VISIBLE_SLOTS - self.slot_padding
        panel_width = inventory_bar_width + 20
        panel_height = 65
        panel_x = x - 10
        panel_rect = pygame.Rect(panel_x, y - 5, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        # Gradient background
        for py in range(panel_height):
            alpha = int(220 - (py / panel_height) * 20)
            pygame.draw.line(panel_surface, (50, 50, 60, alpha), (0, py), (panel_width, py))
        screen.blit(panel_surface, (panel_x, y - 5))
        pygame.draw.rect(screen, (120, 120, 140), panel_rect, 2)
        # Inner highlight
        pygame.draw.line(screen, (80, 80, 100, 100), (panel_x + 2, y - 3), (panel_x + panel_width - 8, y - 3), 1)
        
        # Calculate centered slots position within panel
        slots_start_x = panel_x + (panel_width - inventory_bar_width) // 2
        
        # Title (centered)
        title = self.small_font.render("Inventory", True, WHITE)
        title_x = panel_x + (panel_width - title.get_width()) // 2
        screen.blit(title, (title_x, y))
        
        y += 25
        
        # Draw slots (centered)
        visible_items = player.inventory.get_visible_items()
        for i, (item, count) in enumerate(visible_items):
            slot_x = slots_start_x + (self.slot_size + self.slot_padding) * i
            
            # Draw slot background with depth
            slot_rect = pygame.Rect(slot_x, y, self.slot_size, self.slot_size)
            # Slot shadow
            shadow_rect = pygame.Rect(slot_x + 2, y + 2, self.slot_size, self.slot_size)
            pygame.draw.rect(screen, (20, 20, 20), shadow_rect)
            # Main slot
            pygame.draw.rect(screen, (60, 60, 70), slot_rect)
            # Highlight
            pygame.draw.line(screen, (100, 100, 110), (slot_x, y), (slot_x + self.slot_size - 1, y), 1)
            pygame.draw.line(screen, (100, 100, 110), (slot_x, y), (slot_x, y + self.slot_size - 1), 1)
            # Border
            pygame.draw.rect(screen, (150, 150, 160), slot_rect, 2)
            
            # Draw item if present
            if item:
                # Try to get sprite from asset manager (for dirt and other items with sprites)
                sprite = None
                if self.asset_manager:
                    # Check for item-specific sprite first (e.g., 'dirt')
                    sprite = self.asset_manager.get_sprite(item)
                    # If not found, check for block sprite (e.g., 'block_dirt')
                    if not sprite and item in ['dirt', 'stone', 'copper']:
                        sprite = self.asset_manager.get_sprite(f'block_{item}')
                
                if sprite:
                    # Scale sprite to fit slot (with padding)
                    sprite_size = self.slot_size - 10
                    scaled_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                    screen.blit(scaled_sprite, (slot_x + 5, y + 5))
                else:
                    # Fallback to color rendering
                    item_color = self._get_item_color(item)
                    item_rect = pygame.Rect(slot_x + 5, y + 5, self.slot_size - 10, self.slot_size - 10)
                    pygame.draw.rect(screen, item_color, item_rect)
                
                # Draw count centered at bottom of slot
                count_text = self.small_font.render(str(count), True, WHITE)
                # Center horizontally and position at bottom
                count_x = slot_x + (self.slot_size - count_text.get_width()) // 2
                count_y = y + self.slot_size - count_text.get_height() - 3  # 3 pixels from bottom
                screen.blit(count_text, (count_x, count_y))
        
        # Show "Inventory Full" message if needed (centered)
        if player.inventory.is_full():
            msg = self.small_font.render("INVENTORY FULL", True, RED)
            msg_x = panel_x + (panel_width - msg.get_width()) // 2
            screen.blit(msg, (msg_x, y + self.slot_size + 10))
    
    def render_hp_bar(self, screen, player):
        """Render player HP bar with gold on the right (according to readme)"""
        x, y = self.hp_bar_pos
        bar_width = 300
        bar_height = 28
        
        # Gold text width (to position it on the right end of HP bar)
        gold_text = self.small_font.render(f"Gold: {player.gold}", True, YELLOW)
        gold_width = gold_text.get_width() + 15
        
        # Total panel width (HP bar + gold spacing)
        total_width = bar_width + gold_width + 20
        panel_rect = pygame.Rect(x - 10, y - 5, total_width, bar_height + 10)
        panel_surface = pygame.Surface((total_width, bar_height + 10), pygame.SRCALPHA)
        for py in range(bar_height + 10):
            alpha = int(220 - (py / (bar_height + 10)) * 20)
            pygame.draw.line(panel_surface, (50, 50, 60, alpha), (0, py), (total_width, py))
        screen.blit(panel_surface, (x - 10, y - 5))
        pygame.draw.rect(screen, (120, 120, 140), panel_rect, 2)
        
        # Background bar
        pygame.draw.rect(screen, HP_BAR_BG, (x, y, bar_width, bar_height))
        
        # HP
        hp_percentage = player.hp / player.max_hp
        hp_width = int(bar_width * hp_percentage)
        pygame.draw.rect(screen, HP_BAR_COLOR, (x, y, hp_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 2)
        
        # HP Text (left side)
        hp_text = self.small_font.render(f"HP: {player.hp}/{player.max_hp}", True, WHITE)
        screen.blit(hp_text, (x + 5, y + 6))
        
        # Gold text (right end of HP bar, according to readme)
        gold_x = x + bar_width + 10
        screen.blit(gold_text, (gold_x, y + 6))
    
    def render_title_bar(self, screen):
        """Render title bar with window controls at the top"""
        # Title bar background
        title_bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, self.title_bar_height)
        pygame.draw.rect(screen, (40, 40, 50), title_bar_rect)
        pygame.draw.line(screen, (60, 60, 70), (0, self.title_bar_height - 1), 
                        (SCREEN_WIDTH, self.title_bar_height - 1), 2)
        
        # Title text
        title_text = self.small_font.render("Wild Eldoria", True, WHITE)
        screen.blit(title_text, (10, (self.title_bar_height - title_text.get_height()) // 2))
        
        # Window control buttons (minimize, maximize, close) on the right
        button_x = SCREEN_WIDTH - (self.title_bar_button_size + self.title_bar_button_padding) * 3
        button_y = (self.title_bar_height - self.title_bar_button_size) // 2
        
        # Minimize button
        minimize_rect = pygame.Rect(button_x, button_y, self.title_bar_button_size, self.title_bar_button_size)
        pygame.draw.rect(screen, (60, 60, 70), minimize_rect)
        pygame.draw.rect(screen, (100, 100, 110), minimize_rect, 1)
        # Minimize icon (horizontal line)
        line_y = button_y + self.title_bar_button_size // 2
        pygame.draw.line(screen, WHITE, (button_x + 8, line_y), 
                        (button_x + self.title_bar_button_size - 8, line_y), 2)
        self.title_bar_buttons['minimize'] = minimize_rect
        
        # Maximize/Restore button
        button_x += self.title_bar_button_size + self.title_bar_button_padding
        maximize_rect = pygame.Rect(button_x, button_y, self.title_bar_button_size, self.title_bar_button_size)
        pygame.draw.rect(screen, (60, 60, 70), maximize_rect)
        pygame.draw.rect(screen, (100, 100, 110), maximize_rect, 1)
        # Maximize icon (two overlapping squares)
        margin = 6
        pygame.draw.rect(screen, WHITE, 
                        (button_x + margin, button_y + margin, 
                         self.title_bar_button_size - margin * 2, self.title_bar_button_size - margin * 2), 2)
        pygame.draw.rect(screen, WHITE, 
                        (button_x + margin + 3, button_y + margin + 3, 
                         self.title_bar_button_size - margin * 2 - 3, self.title_bar_button_size - margin * 2 - 3), 2)
        self.title_bar_buttons['maximize'] = maximize_rect
        
        # Close button
        button_x += self.title_bar_button_size + self.title_bar_button_padding
        close_rect = pygame.Rect(button_x, button_y, self.title_bar_button_size, self.title_bar_button_size)
        pygame.draw.rect(screen, (200, 50, 50), close_rect)
        pygame.draw.rect(screen, (255, 100, 100), close_rect, 1)
        # X icon
        margin = 8
        pygame.draw.line(screen, WHITE, (button_x + margin, button_y + margin), 
                        (button_x + self.title_bar_button_size - margin, button_y + self.title_bar_button_size - margin), 2)
        pygame.draw.line(screen, WHITE, (button_x + self.title_bar_button_size - margin, button_y + margin), 
                        (button_x + margin, button_y + self.title_bar_button_size - margin), 2)
        self.title_bar_buttons['close'] = close_rect
    
    def render_exit_button(self, screen):
        """Render exit/quit button in top-right corner"""
        x, y = self.exit_button_pos
        btn_size = 40
        
        # Button background
        btn_rect = pygame.Rect(x, y, btn_size, btn_size)
        pygame.draw.rect(screen, (200, 50, 50), btn_rect)
        pygame.draw.rect(screen, (255, 100, 100), btn_rect, 2)
        
        # X symbol
        margin = 10
        pygame.draw.line(screen, WHITE, (x + margin, y + margin), 
                        (x + btn_size - margin, y + btn_size - margin), 3)
        pygame.draw.line(screen, WHITE, (x + btn_size - margin, y + margin), 
                        (x + margin, y + btn_size - margin), 3)
        
        # Tooltip on hover would go here
        self.exit_button_rect = btn_rect
    
    def render_equipment(self, screen, player):
        """Render equipped items bar (centered at bottom)"""
        x, y = self.equipment_pos
        
        # Background panel
        num_slots = 7
        equipment_bar_width = (self.slot_size + self.slot_padding) * num_slots - self.slot_padding
        panel_width = equipment_bar_width + 20
        panel_height = self.slot_size + 35
        panel_x = x - 10
        panel_y = y - 25
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for py in range(panel_height):
            alpha = int(220 - (py / panel_height) * 20)
            pygame.draw.line(panel_surface, (50, 50, 60, alpha), (0, py), (panel_width, py))
        screen.blit(panel_surface, (panel_x, panel_y))
        pygame.draw.rect(screen, (120, 120, 140), panel_rect, 2)
        
        # Equipment slot labels
        labels = ['Helmet', 'Chest', 'Legs', 'Boots', 'Cons.1', 'Cons.2', 'Weapon']
        slot_keys = ['helmet', 'chestplate', 'leggings', 'boots', 'consumable1', 'consumable2', 'weapon']
        
        # Center slots within panel
        slots_start_x = panel_x + (panel_width - equipment_bar_width) // 2
        
        for i, (label, key) in enumerate(zip(labels, slot_keys)):
            slot_x = slots_start_x + (self.slot_size + self.slot_padding) * i
            
            # Draw slot
            slot_rect = pygame.Rect(slot_x, y, self.slot_size, self.slot_size)
            pygame.draw.rect(screen, DARK_GRAY, slot_rect)
            pygame.draw.rect(screen, LIGHT_GRAY, slot_rect, 2)
            
            # Draw equipped item
            equipped_item = player.equipment.get_item(key)
            if equipped_item:
                item_color = self._get_item_color(equipped_item)
                item_rect = pygame.Rect(slot_x + 5, y + 5, self.slot_size - 10, self.slot_size - 10)
                pygame.draw.rect(screen, item_color, item_rect)
            
            # Draw label above slot
            label_text = self.small_font.render(label, True, WHITE)
            label_rect = label_text.get_rect(center=(slot_x + self.slot_size // 2, y - 8))
            screen.blit(label_text, label_rect)
    
    def render_stats(self, screen, player):
        """Render current stats above equipment bar"""
        x, y = self.stats_pos
        
        # Get stats
        armor = player.equipment.get_total_armor()
        weapon = player.weapon
        
        stats_text = self.small_font.render(
            f"Armor: {armor} | Weapon: {weapon.capitalize()} | DMG: {player.weapon_damage}",
            True, WHITE
        )
        
        # Center the stats text properly
        stats_x = SCREEN_WIDTH // 2 - stats_text.get_width() // 2
        
        # Background panel
        panel_width = stats_text.get_width() + 20
        panel_height = stats_text.get_height() + 10
        panel_rect = pygame.Rect(stats_x - 10, y - 5, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((40, 40, 40, 220))
        screen.blit(panel_surface, (stats_x - 10, y - 5))
        pygame.draw.rect(screen, UI_BORDER_COLOR, panel_rect, 2)
        
        screen.blit(stats_text, (stats_x, y))
    
    def render_platform_text(self, screen):
        """Render platform placement instruction above equipment bar"""
        # Position above stats (which is above equipment bar)
        x, y = self.stats_pos
        text_y = y - 30  # Above stats
        
        platform_text = self.small_font.render(
            "Press Q consume 1 dirt and place a platform",
            True, WHITE
        )
        
        # Center the text
        text_x = SCREEN_WIDTH // 2 - platform_text.get_width() // 2
        
        # Background panel
        panel_width = platform_text.get_width() + 20
        panel_height = platform_text.get_height() + 10
        panel_rect = pygame.Rect(text_x - 10, text_y - 5, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((40, 40, 40, 220))
        screen.blit(panel_surface, (text_x - 10, text_y - 5))
        pygame.draw.rect(screen, UI_BORDER_COLOR, panel_rect, 2)
        
        screen.blit(platform_text, (text_x, text_y))
    
    def render_day_counter(self, screen, day_night_manager):
        """Render survival day counter"""
        day = day_night_manager.get_day_count()
        time_of_day = "Day" if day_night_manager.is_day() else "Night"
        
        day_text = self.small_font.render(f"Day {day}", True, WHITE)
        time_text = self.small_font.render(time_of_day, True, YELLOW if day_night_manager.is_day() else BLUE)
        
        # Use stored position (right edge position)
        right_edge_x, y = self.day_counter_pos
        panel_width = max(day_text.get_width(), time_text.get_width()) + 20
        
        # Calculate x position so right edge is at right_edge_x (30px from screen right)
        x = right_edge_x - panel_width + 10  # +10 to account for panel padding
        
        # Background panel with gradient
        panel_height = 50
        panel_rect = pygame.Rect(x - 10, y - 5, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for py in range(panel_height):
            alpha = int(220 - (py / panel_height) * 20)
            pygame.draw.line(panel_surface, (50, 50, 60, alpha), (0, py), (panel_width, py))
        screen.blit(panel_surface, (x - 10, y - 5))
        pygame.draw.rect(screen, (120, 120, 140), panel_rect, 2)
        
        screen.blit(day_text, (x, y))
        screen.blit(time_text, (x, y + 22))
    
    def render_depth_level(self, screen, depth_level):
        """Render depth level (below day counter)"""
        if depth_level == 0:
            return  # Don't show depth on main map
        
        depth_text = self.small_font.render(f"Depth: {depth_level}", True, WHITE)
        
        # Position below day counter, aligned to right edge
        right_edge_x, y = self.day_counter_pos
        panel_width = depth_text.get_width() + 20
        x = right_edge_x - panel_width + 10  # Align right edge 30px from screen right
        y += 50  # Below day counter panel
        
        panel_width = depth_text.get_width() + 20
        panel_height = 30
        
        # Background panel with gradient
        panel_rect = pygame.Rect(x - 10, y, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for py in range(panel_height):
            alpha = int(220 - (py / panel_height) * 20)
            pygame.draw.line(panel_surface, (50, 50, 60, alpha), (0, py), (panel_width, py))
        screen.blit(panel_surface, (x - 10, y))
        pygame.draw.rect(screen, (120, 120, 140), panel_rect, 2)
        
        screen.blit(depth_text, (x, y + 6))
    
    def render_exploration_timer(self, screen, timer_remaining):
        """Render exploration timer (below depth level)"""
        import math
        
        # Calculate minutes and seconds
        total_seconds = max(0, int(timer_remaining))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        # Format as MM:SS
        timer_text_str = f"{minutes:02d}:{seconds:02d}"
        
        # Check if <= 2 minutes (120 seconds) - make bigger and red
        if total_seconds <= 120:
            # Use larger font (2x size)
            timer_font = pygame.font.Font(None, 36)  # 2x the small_font size (18 * 2)
            timer_color = RED
        else:
            # Normal size
            timer_font = self.small_font
            timer_color = WHITE
        
        timer_text = timer_font.render(timer_text_str, True, timer_color)
        
        # Position below depth level, aligned to right edge
        right_edge_x, y = self.day_counter_pos
        panel_width = timer_text.get_width() + 20
        x = right_edge_x - panel_width + 10  # Align right edge 30px from screen right
        y += 80  # Below depth level panel (50 for day counter + 30 for depth)
        
        panel_height = timer_text.get_height() + 10
        
        # Background panel with gradient
        panel_rect = pygame.Rect(x - 10, y, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for py in range(panel_height):
            alpha = int(220 - (py / panel_height) * 20)
            pygame.draw.line(panel_surface, (50, 50, 60, alpha), (0, py), (panel_width, py))
        screen.blit(panel_surface, (x - 10, y))
        pygame.draw.rect(screen, (120, 120, 140), panel_rect, 2)
        
        screen.blit(timer_text, (x, y + 5))
    
    def render_menu(self, screen, player):
        """Render building interaction menu"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Menu box (centered)
        menu_width = 600
        menu_height = 500
        menu_x = SCREEN_WIDTH // 2 - menu_width // 2
        menu_y = SCREEN_HEIGHT // 2 - menu_height // 2
        
        # Menu background with gradient
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        for py in range(menu_height):
            alpha = int(240 - (py / menu_height) * 20)
            pygame.draw.line(menu_surface, (50, 50, 60, alpha), (0, py), (menu_width, py))
        screen.blit(menu_surface, (menu_x, menu_y))
        pygame.draw.rect(screen, (150, 150, 170), menu_rect, 3)
        
        # Title bar
        title_bar = pygame.Rect(menu_x, menu_y, menu_width, 50)
        pygame.draw.rect(screen, (70, 70, 80), title_bar)
        pygame.draw.line(screen, (100, 100, 120), (menu_x, menu_y + 50), (menu_x + menu_width, menu_y + 50), 2)
        
        # Title
        title = self.font.render(f"{self.active_menu.upper()} Menu", True, WHITE)
        screen.blit(title, (menu_x + 20, menu_y + 15))
        
        # Close button (X in top right)
        close_btn_size = 30
        close_btn_x = menu_x + menu_width - close_btn_size - 10
        close_btn_y = menu_y + 10
        close_btn_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)
        pygame.draw.rect(screen, (200, 50, 50), close_btn_rect)
        pygame.draw.rect(screen, (255, 100, 100), close_btn_rect, 2)
        # X symbol
        pygame.draw.line(screen, WHITE, (close_btn_x + 8, close_btn_y + 8), 
                        (close_btn_x + close_btn_size - 8, close_btn_y + close_btn_size - 8), 3)
        pygame.draw.line(screen, WHITE, (close_btn_x + close_btn_size - 8, close_btn_y + 8), 
                        (close_btn_x + 8, close_btn_y + close_btn_size - 8), 3)
        self.close_button_rect = close_btn_rect
        
        # Menu content based on building type
        if self.active_menu == BUILDING_SMITH:
            self._render_smith_menu(screen, menu_x, menu_y, player)
        elif self.active_menu == BUILDING_TAILOR:
            self._render_tailor_menu(screen, menu_x, menu_y, player)
        elif self.active_menu == BUILDING_WITCH:
            self._render_witch_menu(screen, menu_x, menu_y, player)
        elif self.active_menu == BUILDING_FIREPLACE:
            self._render_fireplace_menu(screen, menu_x, menu_y, player)
        elif self.active_menu == BUILDING_BEDROOM:
            self._render_bedroom_menu(screen, menu_x, menu_y, player)
        
        # Close instruction at bottom
        close_text = self.small_font.render("Press ESC or click X to close", True, LIGHT_GRAY)
        screen.blit(close_text, (menu_x + 20, menu_y + menu_height - 25))
    
    def _render_smith_menu(self, screen, x, y, player):
        """Render smith (weapon upgrade) menu"""
        menu_width = 600
        upgrade_level = self.building_upgrades.get(BUILDING_SMITH, 0)
        
        # Render "Upgrade building" button in top right corner
        upgrade_button_x = x + menu_width - 180 - 20  # 180 is button width, 20 is margin from right
        upgrade_button_y = y + 60
        upgrade_button_width = 180
        upgrade_button_height = 40
        
        # Determine upgrade cost
        if upgrade_level == 0:
            upgrade_cost = 200
        elif upgrade_level == 1:
            upgrade_cost = 900
        else:
            upgrade_cost = None  # Maxed out
        
        upgrade_button_rect = pygame.Rect(upgrade_button_x, upgrade_button_y, upgrade_button_width, upgrade_button_height)
        can_afford_upgrade = upgrade_cost is not None and player.gold >= upgrade_cost
        
        upgrade_button_color = (100, 150, 100) if can_afford_upgrade else (80, 80, 80)
        upgrade_border_color = (150, 200, 150) if can_afford_upgrade else (100, 100, 100)
        
        pygame.draw.rect(screen, upgrade_button_color, upgrade_button_rect)
        pygame.draw.rect(screen, upgrade_border_color, upgrade_button_rect, 2)
        
        upgrade_text = f"Upgrade building ({upgrade_cost}g)" if upgrade_cost else "Upgrade building (MAX)"
        upgrade_text_color = WHITE if can_afford_upgrade else LIGHT_GRAY
        upgrade_text_surface = self.small_font.render(upgrade_text, True, upgrade_text_color)
        screen.blit(upgrade_text_surface, (upgrade_button_x + 10, upgrade_button_y + 12))
        
        self.building_upgrade_button = {
            'rect': upgrade_button_rect,
            'cost': upgrade_cost,
            'can_afford': can_afford_upgrade,
            'building': BUILDING_SMITH
        }
        
        y_offset = 80
        text = self.font.render("Weapon Upgrades", True, WHITE)
        screen.blit(text, (x + 20, y + y_offset))
        
        y_offset += 50
        
        # Define upgrades with costs and damage
        upgrades = [
            ("Iron Sword", 100, 20, 'sword'),
            ("Steel Sword", 250, 30, 'sword'),
            ("Legendary Sword", 500, 45, 'sword')
        ]
        
        self.upgrade_buttons = []
        for i, (name, cost, damage, weapon_type) in enumerate(upgrades):
            # Check if button is unlocked (first button always unlocked, others based on upgrade level)
            is_unlocked = i <= upgrade_level
            button_y = y + y_offset
            button_rect = pygame.Rect(x + 30, button_y, menu_width - 60, 50)
            
            # Check if player can afford (only if unlocked)
            can_afford = is_unlocked and player.gold >= cost
            button_color = (80, 120, 80) if can_afford else (80, 80, 80)
            border_color = (100, 200, 100) if can_afford else (100, 100, 100)
            
            # Draw button
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)
            
            # Draw red cross if locked
            if not is_unlocked:
                cross_size = 20
                cross_x = button_rect.centerx - cross_size // 2
                cross_y = button_rect.centery - cross_size // 2
                pygame.draw.line(screen, RED, (cross_x, cross_y), 
                               (cross_x + cross_size, cross_y + cross_size), 3)
                pygame.draw.line(screen, RED, (cross_x + cross_size, cross_y), 
                               (cross_x, cross_y + cross_size), 3)
            
            # Button text
            if is_unlocked:
                upgrade_text = f"{name} - {cost}g (DMG: {damage})"
            else:
                upgrade_text = f"{name} - LOCKED"
            text_color = WHITE if can_afford else (LIGHT_GRAY if is_unlocked else (100, 100, 100))
            text_surface = self.small_font.render(upgrade_text, True, text_color)
            screen.blit(text_surface, (x + 50, button_y + 15))
            
            # Store button info
            self.upgrade_buttons.append({
                'rect': button_rect,
                'name': name,
                'cost': cost,
                'damage': damage,
                'weapon_type': weapon_type,
                'can_afford': can_afford,
                'is_unlocked': is_unlocked
            })
            
            y_offset += 60
        
        # Add "Sell all resources" button
        y_offset += 20  # Add some spacing
        sell_button_y = y + y_offset
        sell_button_rect = pygame.Rect(x + 30, sell_button_y, menu_width - 60, 50)
        
        # Count resources
        dirt_count = player.inventory.get_item_count('dirt')
        stone_count = player.inventory.get_item_count('stone')
        copper_count = player.inventory.get_item_count('copper')
        total_gold = dirt_count * 1 + stone_count * 2 + copper_count * 15
        
        # Check if player has resources to sell
        has_resources = dirt_count > 0 or stone_count > 0 or copper_count > 0
        button_color = (120, 100, 80) if has_resources else (80, 80, 80)
        border_color = (200, 150, 100) if has_resources else (100, 100, 100)
        
        # Draw button
        pygame.draw.rect(screen, button_color, sell_button_rect)
        pygame.draw.rect(screen, border_color, sell_button_rect, 2)
        
        # Button text
        sell_text = f"Sell all resources ({total_gold}g)"
        if not has_resources:
            sell_text = "Sell all resources (No resources)"
        text_color = WHITE if has_resources else LIGHT_GRAY
        text_surface = self.small_font.render(sell_text, True, text_color)
        screen.blit(text_surface, (x + 50, sell_button_y + 15))
        
        # Store button info
        self.sell_resources_button = {
            'rect': sell_button_rect,
            'has_resources': has_resources,
            'total_gold': total_gold
        }
    
    def _render_tailor_menu(self, screen, x, y, player):
        """Render tailor (armor) menu"""
        menu_width = 600
        upgrade_level = self.building_upgrades.get(BUILDING_TAILOR, 0)
        
        # Render "Upgrade building" button in top right corner
        upgrade_button_x = x + menu_width - 180 - 20  # 180 is button width, 20 is margin from right
        upgrade_button_y = y + 60
        upgrade_button_width = 180
        upgrade_button_height = 40
        
        # Determine upgrade cost
        if upgrade_level == 0:
            upgrade_cost = 200
        elif upgrade_level == 1:
            upgrade_cost = 900
        else:
            upgrade_cost = None  # Maxed out
        
        upgrade_button_rect = pygame.Rect(upgrade_button_x, upgrade_button_y, upgrade_button_width, upgrade_button_height)
        can_afford_upgrade = upgrade_cost is not None and player.gold >= upgrade_cost
        
        upgrade_button_color = (100, 150, 100) if can_afford_upgrade else (80, 80, 80)
        upgrade_border_color = (150, 200, 150) if can_afford_upgrade else (100, 100, 100)
        
        pygame.draw.rect(screen, upgrade_button_color, upgrade_button_rect)
        pygame.draw.rect(screen, upgrade_border_color, upgrade_button_rect, 2)
        
        upgrade_text = f"Upgrade building ({upgrade_cost}g)" if upgrade_cost else "Upgrade building (MAX)"
        upgrade_text_color = WHITE if can_afford_upgrade else LIGHT_GRAY
        upgrade_text_surface = self.small_font.render(upgrade_text, True, upgrade_text_color)
        screen.blit(upgrade_text_surface, (upgrade_button_x + 10, upgrade_button_y + 12))
        
        self.building_upgrade_button = {
            'rect': upgrade_button_rect,
            'cost': upgrade_cost,
            'can_afford': can_afford_upgrade,
            'building': BUILDING_TAILOR
        }
        
        y_offset = 80
        text = self.font.render("Armor & Backpack Upgrades", True, WHITE)
        screen.blit(text, (x + 20, y + y_offset))
        
        y_offset += 50
        
        # Define upgrades
        upgrades = [
            ("Leather Armor Set", 150, 'armor'),
            ("Iron Armor Set", 400, 'armor'),
            ("Backpack Upgrade (+6 slots)", 200, 'backpack')
        ]
        
        self.upgrade_buttons = []
        for i, (name, cost, upgrade_type) in enumerate(upgrades):
            # Check if button is unlocked (first button always unlocked, others based on upgrade level)
            is_unlocked = i <= upgrade_level
            button_y = y + y_offset
            button_rect = pygame.Rect(x + 30, button_y, menu_width - 60, 50)
            
            can_afford = is_unlocked and player.gold >= cost
            button_color = (80, 120, 80) if can_afford else (80, 80, 80)
            border_color = (100, 200, 100) if can_afford else (100, 100, 100)
            
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)
            
            # Draw red cross if locked
            if not is_unlocked:
                cross_size = 20
                cross_x = button_rect.centerx - cross_size // 2
                cross_y = button_rect.centery - cross_size // 2
                pygame.draw.line(screen, RED, (cross_x, cross_y), 
                               (cross_x + cross_size, cross_y + cross_size), 3)
                pygame.draw.line(screen, RED, (cross_x + cross_size, cross_y), 
                               (cross_x, cross_y + cross_size), 3)
            
            if is_unlocked:
                upgrade_text = f"{name} - {cost}g"
            else:
                upgrade_text = f"{name} - LOCKED"
            text_color = WHITE if can_afford else (LIGHT_GRAY if is_unlocked else (100, 100, 100))
            text_surface = self.small_font.render(upgrade_text, True, text_color)
            screen.blit(text_surface, (x + 50, button_y + 15))
            
            self.upgrade_buttons.append({
                'rect': button_rect,
                'name': name,
                'cost': cost,
                'upgrade_type': upgrade_type,
                'can_afford': can_afford,
                'is_unlocked': is_unlocked
            })
            
            y_offset += 60
    
    def _render_witch_menu(self, screen, x, y, player):
        """Render witch (consumables) menu"""
        menu_width = 600
        upgrade_level = self.building_upgrades.get(BUILDING_WITCH, 0)
        
        # Render "Upgrade building" button in top right corner
        upgrade_button_x = x + menu_width - 180 - 20  # 180 is button width, 20 is margin from right
        upgrade_button_y = y + 60
        upgrade_button_width = 180
        upgrade_button_height = 40
        
        # Determine upgrade cost
        if upgrade_level == 0:
            upgrade_cost = 200
        elif upgrade_level == 1:
            upgrade_cost = 900
        else:
            upgrade_cost = None  # Maxed out
        
        upgrade_button_rect = pygame.Rect(upgrade_button_x, upgrade_button_y, upgrade_button_width, upgrade_button_height)
        can_afford_upgrade = upgrade_cost is not None and player.gold >= upgrade_cost
        
        upgrade_button_color = (100, 150, 100) if can_afford_upgrade else (80, 80, 80)
        upgrade_border_color = (150, 200, 150) if can_afford_upgrade else (100, 100, 100)
        
        pygame.draw.rect(screen, upgrade_button_color, upgrade_button_rect)
        pygame.draw.rect(screen, upgrade_border_color, upgrade_button_rect, 2)
        
        upgrade_text = f"Upgrade building ({upgrade_cost}g)" if upgrade_cost else "Upgrade building (MAX)"
        upgrade_text_color = WHITE if can_afford_upgrade else LIGHT_GRAY
        upgrade_text_surface = self.small_font.render(upgrade_text, True, upgrade_text_color)
        screen.blit(upgrade_text_surface, (upgrade_button_x + 10, upgrade_button_y + 12))
        
        self.building_upgrade_button = {
            'rect': upgrade_button_rect,
            'cost': upgrade_cost,
            'can_afford': can_afford_upgrade,
            'building': BUILDING_WITCH
        }
        
        y_offset = 80
        text = self.font.render("Potions & Consumables", True, WHITE)
        screen.blit(text, (x + 20, y + y_offset))
        
        y_offset += 50
        
        # Define potions
        potions = [
            ("Health Potion", 20, 'health'),
            ("Strength Potion", 30, 'strength'),
            ("Speed Potion", 25, 'speed')
        ]
        
        self.upgrade_buttons = []
        for i, (name, cost, potion_type) in enumerate(potions):
            # Check if button is unlocked (first button always unlocked, others based on upgrade level)
            is_unlocked = i <= upgrade_level
            button_y = y + y_offset
            button_rect = pygame.Rect(x + 30, button_y, menu_width - 60, 50)
            
            can_afford = is_unlocked and player.gold >= cost
            button_color = (80, 120, 80) if can_afford else (80, 80, 80)
            border_color = (100, 200, 100) if can_afford else (100, 100, 100)
            
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)
            
            # Draw red cross if locked
            if not is_unlocked:
                cross_size = 20
                cross_x = button_rect.centerx - cross_size // 2
                cross_y = button_rect.centery - cross_size // 2
                pygame.draw.line(screen, RED, (cross_x, cross_y), 
                               (cross_x + cross_size, cross_y + cross_size), 3)
                pygame.draw.line(screen, RED, (cross_x + cross_size, cross_y), 
                               (cross_x, cross_y + cross_size), 3)
            
            if is_unlocked:
                potion_text = f"{name} - {cost}g"
            else:
                potion_text = f"{name} - LOCKED"
            text_color = WHITE if can_afford else (LIGHT_GRAY if is_unlocked else (100, 100, 100))
            text_surface = self.small_font.render(potion_text, True, text_color)
            screen.blit(text_surface, (x + 50, button_y + 15))
            
            self.upgrade_buttons.append({
                'rect': button_rect,
                'name': name,
                'cost': cost,
                'potion_type': potion_type,
                'can_afford': can_afford,
                'is_unlocked': is_unlocked
            })
            
            y_offset += 60
    
    def _render_fireplace_menu(self, screen, x, y, player):
        """Render fireplace (cooking) menu"""
        menu_width = 600
        upgrade_level = self.building_upgrades.get(BUILDING_FIREPLACE, 0)
        
        # Render "Upgrade building" button in top right corner
        upgrade_button_x = x + menu_width - 180 - 20  # 180 is button width, 20 is margin from right
        upgrade_button_y = y + 60
        upgrade_button_width = 180
        upgrade_button_height = 40
        
        # Determine upgrade cost
        if upgrade_level == 0:
            upgrade_cost = 200
        elif upgrade_level == 1:
            upgrade_cost = 900
        else:
            upgrade_cost = None  # Maxed out
        
        upgrade_button_rect = pygame.Rect(upgrade_button_x, upgrade_button_y, upgrade_button_width, upgrade_button_height)
        can_afford_upgrade = upgrade_cost is not None and player.gold >= upgrade_cost
        
        upgrade_button_color = (100, 150, 100) if can_afford_upgrade else (80, 80, 80)
        upgrade_border_color = (150, 200, 150) if can_afford_upgrade else (100, 100, 100)
        
        pygame.draw.rect(screen, upgrade_button_color, upgrade_button_rect)
        pygame.draw.rect(screen, upgrade_border_color, upgrade_button_rect, 2)
        
        upgrade_text = f"Upgrade building ({upgrade_cost}g)" if upgrade_cost else "Upgrade building (MAX)"
        upgrade_text_color = WHITE if can_afford_upgrade else LIGHT_GRAY
        upgrade_text_surface = self.small_font.render(upgrade_text, True, upgrade_text_color)
        screen.blit(upgrade_text_surface, (upgrade_button_x + 10, upgrade_button_y + 12))
        
        self.building_upgrade_button = {
            'rect': upgrade_button_rect,
            'cost': upgrade_cost,
            'can_afford': can_afford_upgrade,
            'building': BUILDING_FIREPLACE
        }
        
        y_offset = 80
        text = self.font.render("Cook Food", True, WHITE)
        screen.blit(text, (x + 20, y + y_offset))
        
        y_offset += 50
        
        # Define food recipes
        recipes = [
            ("Cooked Meat", 10, 'meat'),
            ("Bread", 5, 'bread'),
            ("Stew", 20, 'stew')
        ]
        
        self.upgrade_buttons = []
        for i, (name, cost, food_type) in enumerate(recipes):
            # Check if button is unlocked (first button always unlocked, others based on upgrade level)
            is_unlocked = i <= upgrade_level
            button_y = y + y_offset
            button_rect = pygame.Rect(x + 30, button_y, menu_width - 60, 50)
            
            can_afford = is_unlocked and player.gold >= cost
            button_color = (80, 120, 80) if can_afford else (80, 80, 80)
            border_color = (100, 200, 100) if can_afford else (100, 100, 100)
            
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)
            
            # Draw red cross if locked
            if not is_unlocked:
                cross_size = 20
                cross_x = button_rect.centerx - cross_size // 2
                cross_y = button_rect.centery - cross_size // 2
                pygame.draw.line(screen, RED, (cross_x, cross_y), 
                               (cross_x + cross_size, cross_y + cross_size), 3)
                pygame.draw.line(screen, RED, (cross_x + cross_size, cross_y), 
                               (cross_x, cross_y + cross_size), 3)
            
            if is_unlocked:
                food_text = f"{name} - {cost}g"
            else:
                food_text = f"{name} - LOCKED"
            text_color = WHITE if can_afford else (LIGHT_GRAY if is_unlocked else (100, 100, 100))
            text_surface = self.small_font.render(food_text, True, text_color)
            screen.blit(text_surface, (x + 50, button_y + 15))
            
            self.upgrade_buttons.append({
                'rect': button_rect,
                'name': name,
                'cost': cost,
                'food_type': food_type,
                'can_afford': can_afford,
                'is_unlocked': is_unlocked
            })
            
            y_offset += 60
    
    def _render_bedroom_menu(self, screen, x, y, player):
        """Render bedroom (save) menu"""
        y_offset = 60
        text = self.font.render("Save Game", True, WHITE)
        screen.blit(text, (x + 20, y + y_offset))
        
        y_offset += 40
        save_text = self.small_font.render("Press S to save your progress", True, GREEN)
        screen.blit(save_text, (x + 40, y + y_offset))
    
    def open_building_menu(self, building_type, player):
        """Open building interaction menu"""
        self.active_menu = building_type
        self.upgrade_buttons = []
        self.close_button_rect = None
    
    def close_menu(self):
        """Close active menu"""
        self.active_menu = None
        self.upgrade_buttons = []
        self.close_button_rect = None
        if hasattr(self, 'sell_resources_button'):
            self.sell_resources_button = None
    
    def handle_menu_click(self, pos, player):
        """Handle clicks on menu buttons"""
        if not self.active_menu:
            return False
        
        # Check close button
        if hasattr(self, 'close_button_rect') and self.close_button_rect and self.close_button_rect.collidepoint(pos):
            self.close_menu()
            return True
        
        # Check building upgrade button first
        if hasattr(self, 'building_upgrade_button') and self.building_upgrade_button:
            if self.building_upgrade_button['rect'].collidepoint(pos):
                if self.building_upgrade_button.get('can_afford', False):
                    building = self.building_upgrade_button['building']
                    cost = self.building_upgrade_button['cost']
                    if player.gold >= cost:
                        player.spend_gold(cost)
                        self.building_upgrades[building] += 1
                        return True
        
        # Check upgrade buttons (only if unlocked)
        if hasattr(self, 'upgrade_buttons') and self.upgrade_buttons:
            for button in self.upgrade_buttons:
                if button['rect'].collidepoint(pos):
                    # Only allow purchase if unlocked and can afford
                    if button.get('is_unlocked', True) and button.get('can_afford', False):
                        self._purchase_upgrade(button, player)
                        return True
        
        # Check "Sell all resources" button (only in smith menu)
        if self.active_menu == BUILDING_SMITH:
            if hasattr(self, 'sell_resources_button') and self.sell_resources_button:
                if self.sell_resources_button['rect'].collidepoint(pos) and self.sell_resources_button.get('has_resources', False):
                    self._sell_all_resources(player)
                    return True
        
        return False
    
    def _purchase_upgrade(self, button, player):
        """Handle purchase of upgrade"""
        cost = button['cost']
        if player.gold >= cost:
            player.spend_gold(cost)
            
            # Apply upgrade based on type
            if 'weapon_type' in button:
                # Weapon upgrade
                player.equip_weapon(button['weapon_type'])
                if 'damage' in button:
                    # Update weapon damage (this would need to be implemented in player)
                    pass
            elif 'upgrade_type' in button:
                # Armor or backpack upgrade
                if button['upgrade_type'] == 'armor':
                    # Add armor (would need equipment system)
                    pass
                elif button['upgrade_type'] == 'backpack':
                    # Increase inventory (would need inventory system)
                    pass
            elif 'potion_type' in button:
                # Add potion to inventory
                player.inventory.add_item(button['potion_type'])
            elif 'food_type' in button:
                # Add food to inventory
                player.inventory.add_item(button['food_type'])
    
    def _sell_all_resources(self, player):
        """Sell all dirt, stone, and copper resources"""
        # Get counts
        dirt_count = player.inventory.get_item_count('dirt')
        stone_count = player.inventory.get_item_count('stone')
        copper_count = player.inventory.get_item_count('copper')
        
        # Calculate total gold (dirt: 1g, stone: 2g, copper: 15g)
        total_gold = dirt_count * 1 + stone_count * 2 + copper_count * 15
        
        # Remove all dirt, stone, and copper
        if dirt_count > 0:
            player.inventory.remove_item('dirt', dirt_count)
        if stone_count > 0:
            player.inventory.remove_item('stone', stone_count)
        if copper_count > 0:
            player.inventory.remove_item('copper', copper_count)
        
        # Add gold to player
        if total_gold > 0:
            player.add_gold(total_gold)
    
    def handle_title_bar_click(self, pos):
        """Handle clicks on title bar buttons. Returns action string or None"""
        if not self.title_bar_buttons:
            return None
        
        if 'minimize' in self.title_bar_buttons and self.title_bar_buttons['minimize'].collidepoint(pos):
            return 'minimize'
        elif 'maximize' in self.title_bar_buttons and self.title_bar_buttons['maximize'].collidepoint(pos):
            return 'maximize'
        elif 'close' in self.title_bar_buttons and self.title_bar_buttons['close'].collidepoint(pos):
            return 'close'
        return None
    
    def handle_click(self, pos, player):
        """Handle mouse clicks on UI elements"""
        # Check inventory clicks
        # Check equipment clicks
        # Check menu buttons
        pass
    
    def _get_item_color(self, item):
        """Get color for item type (placeholder)"""
        colors = {
            'stone': GRAY,
            'dirt': (139, 69, 19),
            'copper': (144, 238, 144),  # Light green
            'wood': (101, 67, 33),
            'sword': (192, 192, 192),
            'wand': (138, 43, 226),
            'bow': (139, 69, 19),
            'club': (101, 67, 33),
            'coin': YELLOW
        }
        return colors.get(item, WHITE)