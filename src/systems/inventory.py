"""
src/systems/inventory.py
Inventory management system
"""

class Inventory:
    def __init__(self, total_slots):
        self.visible_slots = 6
        self.hidden_slots = total_slots - self.visible_slots
        self.items = [None] * total_slots
        self.item_counts = [0] * total_slots
    
    def add_item(self, item_type, count=1):
        """
        Add item to inventory, returns True if successful
        Fills visible slots first, then hidden slots
        """
        # Try to stack with existing items
        for i in range(len(self.items)):
            if self.items[i] == item_type:
                self.item_counts[i] += count
                return True
        
        # Find first empty slot
        for i in range(len(self.items)):
            if self.items[i] is None:
                self.items[i] = item_type
                self.item_counts[i] = count
                return True
        
        # Inventory full
        return False
    
    def remove_item(self, item_type, count=1):
        """Remove item from inventory, returns True if successful"""
        for i in range(len(self.items)):
            if self.items[i] == item_type:
                if self.item_counts[i] >= count:
                    self.item_counts[i] -= count
                    if self.item_counts[i] == 0:
                        self.items[i] = None
                    return True
        return False
    
    def has_item(self, item_type, count=1):
        """Check if inventory has enough of an item"""
        total = 0
        for i in range(len(self.items)):
            if self.items[i] == item_type:
                total += self.item_counts[i]
        return total >= count
    
    def get_item_count(self, item_type):
        """Get total count of an item"""
        total = 0
        for i in range(len(self.items)):
            if self.items[i] == item_type:
                total += self.item_counts[i]
        return total
    
    def get_visible_items(self):
        """Get items in visible slots"""
        return list(zip(
            self.items[:self.visible_slots], 
            self.item_counts[:self.visible_slots]
        ))
    
    def get_all_items(self):
        """Get all items including hidden"""
        return list(zip(self.items, self.item_counts))
    
    def is_full(self):
        """Check if inventory is completely full"""
        return all(item is not None for item in self.items)