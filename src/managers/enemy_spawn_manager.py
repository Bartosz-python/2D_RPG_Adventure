"""
src/managers/enemy_spawn_manager.py
Enemy spawn system with day/night/depth conditions
"""
from src.config.settings import *
from src.entities.enemy import Enemy

class EnemySpawnManager:
    def __init__(self):
        # Enemy spawn configurations
        # Each entry: {
        #   'enemy_type': str,
        #   'spawn_conditions': {
        #       'day': bool,  # True = can spawn during day, False = cannot
        #       'night': bool,  # True = can spawn during night, False = cannot
        #       'min_depth': int,  # Minimum depth level (blocks below spawn)
        #       'max_depth': int or None  # Maximum depth level (None = no limit)
        #   },
        #   'spawn_rate': float,  # Probability per spawn check (0.0 to 1.0)
        #   'spawn_interval': float,  # Seconds between spawn checks
        #   'max_count': int  # Maximum enemies of this type on map
        # }
        self.enemy_configs = {}
        self.spawn_timers = {}  # Track spawn timers for each enemy type
        self.last_spawn_check = {}  # Track last spawn check time
    
    def register_enemy_type(self, enemy_type, spawn_conditions, spawn_rate=0.1, 
                           spawn_interval=5.0, max_count=5, sprite_path=None):
        """Register an enemy type with spawn conditions
        Args:
            enemy_type: Type identifier for the enemy
            spawn_conditions: Dict with 'day', 'night', 'min_depth', 'max_depth'
            spawn_rate: Probability of spawning (0.0 to 1.0)
            spawn_interval: Seconds between spawn attempts
            max_count: Maximum enemies of this type on map
            sprite_path: Optional custom sprite path for enemy graphics
        """
        self.enemy_configs[enemy_type] = {
            'spawn_conditions': spawn_conditions,
            'spawn_rate': spawn_rate,
            'spawn_interval': spawn_interval,
            'max_count': max_count,
            'sprite_path': sprite_path
        }
        self.spawn_timers[enemy_type] = 0.0
        self.last_spawn_check[enemy_type] = 0.0
    
    def can_spawn(self, enemy_type, is_day, current_depth):
        """Check if enemy can spawn based on conditions"""
        if enemy_type not in self.enemy_configs:
            return False
        
        config = self.enemy_configs[enemy_type]
        conditions = config['spawn_conditions']
        
        # Check day/night condition
        if is_day and not conditions.get('day', True):
            return False
        if not is_day and not conditions.get('night', True):
            return False
        
        # Check depth condition
        min_depth = conditions.get('min_depth', 0)
        max_depth = conditions.get('max_depth', None)
        
        if current_depth < min_depth:
            return False
        if max_depth is not None and current_depth > max_depth:
            return False
        
        return True
    
    def update(self, dt, game_map, day_night_manager, player_spawn_y, current_player_y):
        """Update spawn system and spawn enemies if conditions are met"""
        if not day_night_manager:
            return
        
        is_day = day_night_manager.is_day()
        # Calculate depth: blocks below spawn point (positive = below spawn)
        depth = max(0, int((current_player_y - player_spawn_y) / TILE_SIZE))
        
        for enemy_type, config in self.enemy_configs.items():
            # Update spawn timer
            self.spawn_timers[enemy_type] += dt
            
            # Check if it's time to attempt spawn
            if self.spawn_timers[enemy_type] >= config['spawn_interval']:
                self.spawn_timers[enemy_type] = 0.0
                
                # Count existing enemies of this type
                existing_count = sum(1 for e in game_map.enemies if e.enemy_type == enemy_type)
                
                # Check if we can spawn (conditions + max count)
                if (existing_count < config['max_count'] and 
                    self.can_spawn(enemy_type, is_day, depth)):
                    
                    # Roll for spawn
                    import random
                    if random.random() < config['spawn_rate']:
                        sprite_path = config.get('sprite_path', None)
                        self._spawn_enemy(enemy_type, game_map, current_player_y, sprite_path)
    
    def _spawn_enemy(self, enemy_type, game_map, player_y, sprite_path=None):
        """Spawn an enemy near the player"""
        import random
        
        # Spawn at random position on map (will be improved to spawn near player)
        spawn_x = random.randint(0, game_map.width - 1)
        spawn_y = random.randint(0, game_map.height - 1)
        
        # Convert to pixel coordinates and spawn
        game_map.spawn_enemy(spawn_x, spawn_y, enemy_type, sprite_path)

