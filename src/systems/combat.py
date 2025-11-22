"""
src/systems/combat.py
Combat system for damage calculation and effects
"""

class CombatSystem:
    @staticmethod
    def calculate_damage(base_damage, weapon_modifier=1.0, armor_reduction=0):
        """Calculate final damage after modifiers"""
        damage = base_damage * weapon_modifier
        damage = max(1, damage - armor_reduction)
        return int(damage)
    
    @staticmethod
    def calculate_knockback(attacker_pos, target_pos, force=200):
        """Calculate knockback vector"""
        dx = target_pos[0] - attacker_pos[0]
        dy = target_pos[1] - attacker_pos[1]
        
        # Normalize and apply force
        distance = max(1, (dx**2 + dy**2)**0.5)
        knockback_x = (dx / distance) * force
        knockback_y = (dy / distance) * force * 0.5  # Less vertical knockback
        
        return knockback_x, knockback_y
    
    @staticmethod
    def is_critical_hit(chance=0.1):
        """Check for critical hit"""
        import random
        return random.random() < chance