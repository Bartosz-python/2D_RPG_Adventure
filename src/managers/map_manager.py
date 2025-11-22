"""
src/managers/map_manager.py
Map loading and management
"""
from src.world.map import Map
from src.config.settings import *

class MapManager:
    def __init__(self, asset_manager):
        self.asset_manager = asset_manager
        self.maps = {}
        self.current_map = None
    
    def load_map(self, map_type):
        """Load or create a map"""
        if map_type in self.maps:
            return self.maps[map_type]
        
        if map_type == MAP_MAIN:
            new_map = self._create_main_map()
        elif map_type == MAP_EXPLORATION:
            new_map = self._create_exploration_map()
        else:
            new_map = Map(40, 30, self.asset_manager)
        
        self.maps[map_type] = new_map
        self.current_map = new_map
        return new_map
    
    def _create_main_map(self):
        """Create main village map"""
        from src.world.map import Map
        game_map = Map(50, 30, self.asset_manager, map_type=MAP_MAIN)
        
        # Ground blocks for collision (invisible, green block is rendered separately)
        # Ground starts at y=25 (in grid coordinates)
        ground_y = 25
        for x in range(50):
            for y in range(ground_y, 30):
                game_map.add_block(x, y, 'stone', destructible=False)
        
        # Add buildings aligned to top of green ground block
        # Ground is at y=25, buildings should be on top edge of ground
        # Building height is 3 tiles, so place them at y=22 to sit on ground
        building_y = 22
        game_map.add_building(10, building_y, BUILDING_BEDROOM)
        game_map.add_building(20, building_y, BUILDING_SMITH)
        game_map.add_building(30, building_y, BUILDING_TAILOR)
        game_map.add_building(40, building_y, BUILDING_WITCH)
        game_map.add_building(15, building_y, BUILDING_FIREPLACE)
        
        # Add exit to exploration above top edge of green block on right side
        # Portal should be at top edge of green block (y=25), but visually above it
        # Exit is 2 tiles tall, so place it at y=23 to align with top edge
        game_map.add_exit(45, 23, "exploration")  # Right side of map, above green block
        
        return game_map
    
    def _create_exploration_map(self):
        """Create exploration map with enemies and resources"""
        from src.world.map import Map
        game_map = Map(80, 40, self.asset_manager)
        
        # Add ground
        for x in range(80):
            for y in range(35, 40):
                game_map.add_block(x, y, 'stone', destructible=False)
        
        # Add destructible blocks (resources)
        import random
        for x in range(0, 80, 3):
            for y in range(30, 35):
                if random.random() < 0.6:
                    block_type = random.choice(['stone', 'dirt'])
                    game_map.add_block(x, y, block_type, destructible=True)
        
        # Add enemies
        game_map.spawn_enemy(30, 30, 'goblin')
        game_map.spawn_enemy(50, 30, 'skeleton')
        game_map.spawn_enemy(70, 30, 'orc')
        
        # Add exit back to main
        game_map.add_exit(5, 34, "main")
        
        return game_map
    
    def get_current_map(self):
        """Get currently active map"""
        return self.current_map