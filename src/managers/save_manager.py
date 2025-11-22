"""
src/managers/save_manager.py
Save and load game state
"""
import json
import os
from src.config.settings import *

class SaveManager:
    def __init__(self, save_file="save_data.json"):
        self.save_file = save_file
    
    def save_game(self, player, day_night_manager, quest_manager, current_map_type):
        """Save game state to file"""
        save_data = {
            'player': {
                'hp': player.hp,
                'max_hp': player.max_hp,
                'gold': player.gold,
                'position': [player.rect.x, player.rect.y],
                'weapon': player.weapon,
                'weapon_damage': player.weapon_damage,
                'inventory': {
                    'items': player.inventory.items,
                    'counts': player.inventory.item_counts
                },
                'equipment': player.equipment.get_all_equipped()
            },
            'day_night': {
                'time': day_night_manager.time,
                'day_count': day_night_manager.day_count,
                'last_day': day_night_manager.last_day
            },
            'quests': {
                'tutorial_complete': quest_manager.tutorial_complete,
                'tutorial_stage': quest_manager.tutorial_stage,
                'completed_quests': [q['name'] if isinstance(q, dict) else q for q in quest_manager.completed_quests]
            },
            'game_state': {
                'current_map': current_map_type
            }
        }
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            print(f"Game saved successfully to {self.save_file}")
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False
    
    def load_game(self, player, day_night_manager, quest_manager):
        """Load game state from file"""
        if not os.path.exists(self.save_file):
            print("No save file found")
            return None
        
        try:
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            # Restore player
            player.hp = save_data['player']['hp']
            player.max_hp = save_data['player']['max_hp']
            player.gold = save_data['player']['gold']
            player.rect.x, player.rect.y = save_data['player']['position']
            player.weapon = save_data['player']['weapon']
            player.weapon_damage = save_data['player']['weapon_damage']
            player.inventory.items = save_data['player']['inventory']['items']
            player.inventory.item_counts = save_data['player']['inventory']['counts']
            
            for slot, item in save_data['player']['equipment'].items():
                player.equipment.slots[slot] = item
            
            # Restore day/night
            day_night_manager.time = save_data['day_night']['time']
            day_night_manager.day_count = save_data['day_night']['day_count']
            day_night_manager.last_day = save_data['day_night']['last_day']
            
            # Restore quests
            quest_manager.tutorial_complete = save_data['quests']['tutorial_complete']
            quest_manager.tutorial_stage = save_data['quests']['tutorial_stage']
            quest_manager.completed_quests = save_data['quests']['completed_quests']
            
            # Return current map type
            print("Game loaded successfully")
            return save_data['game_state']['current_map']
            
        except Exception as e:
            print(f"Load failed: {e}")
            return None
    
    def save_exists(self):
        """Check if save file exists"""
        return os.path.exists(self.save_file)
    
    def delete_save(self):
        """Delete save file"""
        if self.save_exists():
            try:
                os.remove(self.save_file)
                print("Save file deleted")
                return True
            except Exception as e:
                print(f"Failed to delete save: {e}")
                return False
        return False
    
    def get_save_info(self):
        """Get basic info about save file"""
        if not self.save_exists():
            return None
        
        try:
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            return {
                'player_hp': save_data['player']['hp'],
                'gold': save_data['player']['gold'],
                'day': save_data['day_night']['day_count'],
                'weapon': save_data['player']['weapon']
            }
        except:
            return None