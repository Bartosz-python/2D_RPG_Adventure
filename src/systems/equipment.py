"""
src/systems/equipment.py
Equipment management system
"""

class Equipment:
    def __init__(self):
        self.slots = {
            'helmet': None,
            'chestplate': None,
            'leggings': None,
            'boots': None,
            'consumable1': None,
            'consumable2': None,
            'weapon': None
        }
        
        # Armor values for each piece
        self.armor_values = {
            'helmet': 0,
            'chestplate': 0,
            'leggings': 0,
            'boots': 0
        }
    
    def equip(self, slot, item):
        """Equip an item to a slot"""
        if slot in self.slots:
            old_item = self.slots[slot]
            self.slots[slot] = item
            return old_item
        return None
    
    def unequip(self, slot):
        """Remove item from slot"""
        if slot in self.slots:
            item = self.slots[slot]
            self.slots[slot] = None
            return item
        return None
    
    def get_item(self, slot):
        """Get item in slot"""
        return self.slots.get(slot, None)
    
    def get_total_armor(self):
        """Calculate total armor from equipped pieces"""
        total = 0
        for slot in ['helmet', 'chestplate', 'leggings', 'boots']:
            if self.slots[slot]:
                total += self.armor_values.get(slot, 0)
        return total
    
    def set_armor_value(self, slot, value):
        """Set armor value for a piece"""
        if slot in self.armor_values:
            self.armor_values[slot] = value
    
    def get_all_equipped(self):
        """Get dictionary of all equipped items"""
        return self.slots.copy()