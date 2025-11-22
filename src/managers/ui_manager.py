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
        
        # Slot size (define first, used in position calculations)
        self.slot_size = 50
        self.slot_padding = 5
        
        # UI element positions (centered and fully visible with padding)
        padding = 70  # Safe padding from screen edges
        
        # Top-left corner: Inventory (centered horizontally in left quarter)
        inventory_bar_width = (self.slot_size + self.slot_padding) * VISIBLE_SLOTS - self.slot_padding
        inventory_x = padding + (SCREEN_WIDTH // 4 - inventory_bar_width)
        self.inventory_pos = (inventory_x, padding)
        
        # HP bar below inventory (centered with inventory)
        hp_bar_width = 350
        hp_bar_x = inventory_x + (inventory_bar_width - hp_bar_width) // 2
        self.hp_bar_pos = (hp_bar_x, padding + 90)  # Below inventory
        
        # Top-right corner: Exit button and Day counter (stacked)
        exit_btn_size = 40
        self.exit_button_pos = (SCREEN_WIDTH - exit_btn_size - padding, padding)
        self.exit_button_rect = None
        
        # Day counter below exit button
        day_counter_width = 150
        self.day_counter_pos = (SCREEN_WIDTH - day_counter_width - padding, padding + exit_btn_size + 10)
        
        # Bottom-center: Stats and Equipment (centered, properly spaced)
        equipment_bar_width = (self.slot_size + self.slot_padding) * 7 - self.slot_padding
        equipment_x = SCREEN_WIDTH // 2 - equipment_bar_width // 2
        bottom_margin = padding
        self.equipment_pos = (equipment_x, SCREEN_HEIGHT - bottom_margin - self.slot_size - 30)
        
        # Stats above equipment bar (centered)
        stats_width = 500
        stats_x = SCREEN_WIDTH // 2 - stats_width // 2
        self.stats_pos = (stats_x, SCREEN_HEIGHT - bottom_margin - self.slot_size - 75)
    
    def render(self, screen, player, day_night_manager):
        """Render all UI elements"""
        self.render_inventory(screen, player)
        self.render_hp_bar(screen, player)  # Gold is now in HP bar
        self.render_equipment(screen, player)
        self.render_stats(screen, player)
        self.render_day_counter(screen, day_night_manager)
        self.render_exit_button(screen)
        
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
        panel_rect = pygame.Rect(x - 10, y - 5, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        # Gradient background
        for py in range(panel_height):
            alpha = int(220 - (py / panel_height) * 20)
            pygame.draw.line(panel_surface, (50, 50, 60, alpha), (0, py), (panel_width, py))
        screen.blit(panel_surface, (x - 10, y - 5))
        pygame.draw.rect(screen, (120, 120, 140), panel_rect, 2)
        # Inner highlight
        pygame.draw.line(screen, (80, 80, 100, 100), (x - 8, y - 3), (x + panel_width - 12, y - 3), 1)
        
        # Calculate centered slots position
        slots_start_x = x + (panel_width - inventory_bar_width) // 2
        
        # Title (centered)
        title = self.small_font.render("Inventory", True, WHITE)
        title_x = x + (panel_width - title.get_width()) // 2
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
                # Placeholder item rendering
                item_color = self._get_item_color(item)
                item_rect = pygame.Rect(slot_x + 5, y + 5, self.slot_size - 10, self.slot_size - 10)
                pygame.draw.rect(screen, item_color, item_rect)
                
                # Draw count
                count_text = self.small_font.render(str(count), True, WHITE)
                screen.blit(count_text, (slot_x + self.slot_size - 20, y + self.slot_size - 20))
        
        # Show "Inventory Full" message if needed (centered)
        if player.inventory.is_full():
            msg = self.small_font.render("INVENTORY FULL", True, RED)
            msg_x = x + (panel_width - msg.get_width()) // 2
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
        panel_rect = pygame.Rect(x - 10, y - 25, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for py in range(panel_height):
            alpha = int(220 - (py / panel_height) * 20)
            pygame.draw.line(panel_surface, (50, 50, 60, alpha), (0, py), (panel_width, py))
        screen.blit(panel_surface, (x - 10, y - 25))
        pygame.draw.rect(screen, (120, 120, 140), panel_rect, 2)
        
        # Equipment slot labels
        labels = ['Helmet', 'Chest', 'Legs', 'Boots', 'Cons.1', 'Cons.2', 'Weapon']
        slot_keys = ['helmet', 'chestplate', 'leggings', 'boots', 'consumable1', 'consumable2', 'weapon']
        
        # Center slots within panel
        slots_start_x = x + (panel_width - equipment_bar_width) // 2
        
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
    
    def render_day_counter(self, screen, day_night_manager):
        """Render survival day counter"""
        day = day_night_manager.get_day_count()
        time_of_day = "Day" if day_night_manager.is_day() else "Night"
        
        day_text = self.small_font.render(f"Day {day}", True, WHITE)
        time_text = self.small_font.render(time_of_day, True, YELLOW if day_night_manager.is_day() else BLUE)
        
        # Use stored position
        x, y = self.day_counter_pos
        panel_width = max(day_text.get_width(), time_text.get_width()) + 20
        
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
            button_y = y + y_offset
            button_rect = pygame.Rect(x + 30, button_y, menu_width - 60, 50)
            
            # Check if player can afford
            can_afford = player.gold >= cost
            button_color = (80, 120, 80) if can_afford else (80, 80, 80)
            border_color = (100, 200, 100) if can_afford else (100, 100, 100)
            
            # Draw button
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)
            
            # Button text
            upgrade_text = f"{name} - {cost}g (DMG: {damage})"
            text_color = WHITE if can_afford else LIGHT_GRAY
            text_surface = self.small_font.render(upgrade_text, True, text_color)
            screen.blit(text_surface, (x + 50, button_y + 15))
            
            # Store button info
            self.upgrade_buttons.append({
                'rect': button_rect,
                'name': name,
                'cost': cost,
                'damage': damage,
                'weapon_type': weapon_type,
                'can_afford': can_afford
            })
            
            y_offset += 60
    
    def _render_tailor_menu(self, screen, x, y, player):
        """Render tailor (armor) menu"""
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
        menu_width = 600  # Same as in render_menu
        for i, (name, cost, upgrade_type) in enumerate(upgrades):
            button_y = y + y_offset
            button_rect = pygame.Rect(x + 30, button_y, menu_width - 60, 50)
            
            can_afford = player.gold >= cost
            button_color = (80, 120, 80) if can_afford else (80, 80, 80)
            border_color = (100, 200, 100) if can_afford else (100, 100, 100)
            
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)
            
            upgrade_text = f"{name} - {cost}g"
            text_color = WHITE if can_afford else LIGHT_GRAY
            text_surface = self.small_font.render(upgrade_text, True, text_color)
            screen.blit(text_surface, (x + 50, button_y + 15))
            
            self.upgrade_buttons.append({
                'rect': button_rect,
                'name': name,
                'cost': cost,
                'upgrade_type': upgrade_type,
                'can_afford': can_afford
            })
            
            y_offset += 60
    
    def _render_witch_menu(self, screen, x, y, player):
        """Render witch (consumables) menu"""
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
        menu_width = 600
        for i, (name, cost, potion_type) in enumerate(potions):
            button_y = y + y_offset
            button_rect = pygame.Rect(x + 30, button_y, menu_width - 60, 50)
            
            can_afford = player.gold >= cost
            button_color = (80, 120, 80) if can_afford else (80, 80, 80)
            border_color = (100, 200, 100) if can_afford else (100, 100, 100)
            
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)
            
            potion_text = f"{name} - {cost}g"
            text_color = WHITE if can_afford else LIGHT_GRAY
            text_surface = self.small_font.render(potion_text, True, text_color)
            screen.blit(text_surface, (x + 50, button_y + 15))
            
            self.upgrade_buttons.append({
                'rect': button_rect,
                'name': name,
                'cost': cost,
                'potion_type': potion_type,
                'can_afford': can_afford
            })
            
            y_offset += 60
    
    def _render_fireplace_menu(self, screen, x, y, player):
        """Render fireplace (cooking) menu"""
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
        menu_width = 600
        for i, (name, cost, food_type) in enumerate(recipes):
            button_y = y + y_offset
            button_rect = pygame.Rect(x + 30, button_y, menu_width - 60, 50)
            
            can_afford = player.gold >= cost
            button_color = (80, 120, 80) if can_afford else (80, 80, 80)
            border_color = (100, 200, 100) if can_afford else (100, 100, 100)
            
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)
            
            food_text = f"{name} - {cost}g"
            text_color = WHITE if can_afford else LIGHT_GRAY
            text_surface = self.small_font.render(food_text, True, text_color)
            screen.blit(text_surface, (x + 50, button_y + 15))
            
            self.upgrade_buttons.append({
                'rect': button_rect,
                'name': name,
                'cost': cost,
                'food_type': food_type,
                'can_afford': can_afford
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
    
    def handle_menu_click(self, pos, player):
        """Handle clicks on menu buttons"""
        if not self.active_menu:
            return False
        
        # Check close button
        if hasattr(self, 'close_button_rect') and self.close_button_rect and self.close_button_rect.collidepoint(pos):
            self.close_menu()
            return True
        
        # Check upgrade buttons
        if hasattr(self, 'upgrade_buttons') and self.upgrade_buttons:
            for button in self.upgrade_buttons:
                if button['rect'].collidepoint(pos) and button.get('can_afford', False):
                    self._purchase_upgrade(button, player)
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
            'wood': (101, 67, 33),
            'sword': (192, 192, 192),
            'wand': (138, 43, 226),
            'bow': (139, 69, 19),
            'club': (101, 67, 33),
            'coin': YELLOW
        }
        return colors.get(item, WHITE)