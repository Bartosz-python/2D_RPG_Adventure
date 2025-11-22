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
        """Create exploration map with platform of destroyable blocks"""
        from src.world.map import Map
        # 8 screen lengths: 1920 * 8 / 32 = 480 tiles
        map_width = (SCREEN_WIDTH * 8) // TILE_SIZE
        # Increase depth by 4 screen lengths: 1080 * 4 / 32 = 135 tiles
        # Original height was 40, so new height is 40 + 135 = 175 tiles
        map_height = 40 + (SCREEN_HEIGHT * 4) // TILE_SIZE
        game_map = Map(map_width, map_height, self.asset_manager, map_type=MAP_EXPLORATION)
        
        # Create platform of destroyable square blocks
        # Platform starts at y=30 and goes up a few rows
        platform_start_y = 30
        platform_height = 5  # 5 rows of blocks
        
        # Player spawns at y=33 in exploration map (from game.py check_map_transitions)
        # Depth level = (block_y - spawn_y) / TILE_SIZE = (y - 33)
        spawn_y = 33
        
        # Helper function to get block type based on depth
        def get_block_type_by_depth(block_y):
            """Get block type based on depth level with probability ratios"""
            import random
            depth = block_y - spawn_y
            
            if depth <= 10:
                # Above depth 10: 95% dirt, 5% stone
                return 'dirt' if random.random() < 0.95 else 'stone'
            elif depth <= 25:
                # Depth 11-25: 80% dirt, 20% stone
                return 'dirt' if random.random() < 0.80 else 'stone'
            elif depth <= 70:
                # Depth 26-70: 20% dirt, 80% stone
                return 'dirt' if random.random() < 0.20 else 'stone'
            else:
                # Below depth 71: 2% dirt, 98% stone
                return 'dirt' if random.random() < 0.02 else 'stone'
        
        # Fill entire platform with destroyable blocks
        # Blocks are 2x2 size, so place them at 2x2 intervals (every other grid position)
        for x in range(0, map_width, 2):  # Step by 2 for 2x2 blocks
            for y in range(platform_start_y, platform_start_y + platform_height, 2):  # Step by 2
                block_type = get_block_type_by_depth(y)
                game_map.add_block(x, y, block_type, destructible=True)
        
        # Fill the gap left by removing indestructible ground (y=35-40) with destroyable blocks
        # Blocks are 2x2 size, so place them at 2x2 intervals
        for x in range(0, map_width, 2):  # Step by 2 for 2x2 blocks
            for y in range(36, 40, 2):  # Fill y=36 and y=38 (2x2 blocks cover 2 rows each)
                block_type = get_block_type_by_depth(y)
                game_map.add_block(x, y, block_type, destructible=True)
        
        # Fill new depth (from y=40 to bottom) with destroyable blocks
        # Blocks are 2x2 size, so place them at 2x2 intervals
        for x in range(0, map_width, 2):  # Step by 2 for 2x2 blocks
            for y in range(40, map_height - 1, 2):  # Step by 2, leave last row for dark block
                block_type = get_block_type_by_depth(y)
                game_map.add_block(x, y, block_type, destructible=True)
        
        # Add unbreakable dark block across the whole bottom edge
        bottom_y = map_height - 1
        for x in range(map_width):
            game_map.add_block(x, bottom_y, 'stone', destructible=False)
        
        # Add exit back to main
        game_map.add_exit(5, 34, "main")
        
        return game_map
    
    def get_current_map(self):
        """Get currently active map"""
        return self.current_map