"""
src/systems/crafting.py
Crafting system for recipes and item creation
"""

class CraftingSystem:
    def __init__(self):
        self.recipes = self._load_recipes()
    
    def _load_recipes(self):
        """Define crafting recipes"""
        return {
            'wooden_sword': {
                'ingredients': {'wood': 2, 'stone': 1},
                'result': 'wooden_sword',
                'result_count': 1,
                'station': 'smith'
            },
            'leather_helmet': {
                'ingredients': {'leather': 3},
                'result': 'leather_helmet',
                'result_count': 1,
                'station': 'tailor'
            },
            'health_potion': {
                'ingredients': {'herb': 2, 'water': 1},
                'result': 'health_potion',
                'result_count': 1,
                'station': 'witch'
            },
            'cooked_meat': {
                'ingredients': {'raw_meat': 1},
                'result': 'cooked_meat',
                'result_count': 1,
                'station': 'fireplace'
            }
        }
    
    def can_craft(self, recipe_name, inventory):
        """Check if player has ingredients for recipe"""
        if recipe_name not in self.recipes:
            return False
        
        recipe = self.recipes[recipe_name]
        for ingredient, count in recipe['ingredients'].items():
            if not inventory.has_item(ingredient, count):
                return False
        return True
    
    def craft(self, recipe_name, inventory):
        """Craft item if possible, returns crafted item or None"""
        if not self.can_craft(recipe_name, inventory):
            return None
        
        recipe = self.recipes[recipe_name]
        
        # Remove ingredients
        for ingredient, count in recipe['ingredients'].items():
            inventory.remove_item(ingredient, count)
        
        # Add result
        if inventory.add_item(recipe['result'], recipe['result_count']):
            return recipe['result']
        else:
            # Inventory full, return ingredients
            for ingredient, count in recipe['ingredients'].items():
                inventory.add_item(ingredient, count)
            return None
    
    def get_recipes_for_station(self, station):
        """Get all recipes for a crafting station"""
        return {
            name: recipe 
            for name, recipe in self.recipes.items() 
            if recipe['station'] == station
        }
    
    def get_all_recipes(self):
        """Get all crafting recipes"""
        return self.recipes.copy()