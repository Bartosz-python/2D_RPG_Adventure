"""
src/utils/animation.py
Animation system for sprites
"""
import pygame

class Animation:
    def __init__(self, frames, frame_duration=0.1):
        """
        frames: List of pygame.Surface objects
        frame_duration: Time per frame in seconds
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.time_elapsed = 0
        self.loop = True
        self.finished = False
    
    def update(self, dt):
        """Update animation"""
        if self.finished and not self.loop:
            return
        
        self.time_elapsed += dt
        
        if self.time_elapsed >= self.frame_duration:
            self.time_elapsed = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
    
    def get_current_frame(self):
        """Get current frame surface"""
        if not self.frames:
            return None
        return self.frames[self.current_frame]
    
    def reset(self):
        """Reset animation"""
        self.current_frame = 0
        self.time_elapsed = 0
        self.finished = False
    
    def set_loop(self, loop):
        """Set loop behavior"""
        self.loop = loop

class AnimationController:
    def __init__(self):
        self.animations = {}
        self.current_animation = None
    
    def add_animation(self, name, animation):
        """Add animation to controller"""
        self.animations[name] = animation
    
    def play(self, name, force_restart=False):
        """Play animation by name"""
        if name in self.animations:
            if self.current_animation != name or force_restart:
                self.animations[name].reset()
                self.current_animation = name
    
    def update(self, dt):
        """Update current animation"""
        if self.current_animation and self.current_animation in self.animations:
            self.animations[self.current_animation].update(dt)
    
    def get_current_frame(self):
        """Get current frame"""
        if self.current_animation and self.current_animation in self.animations:
            return self.animations[self.current_animation].get_current_frame()
        return None
    
    def is_finished(self):
        """Check if current animation is finished"""
        if self.current_animation and self.current_animation in self.animations:
            return self.animations[self.current_animation].finished
        return False

class SpriteSheet:
    """Load and parse sprite sheets"""
    def __init__(self, image_path, sprite_width, sprite_height):
        self.sheet = pygame.image.load(image_path).convert_alpha()
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
    
    def get_sprite(self, x, y):
        """Get sprite at grid position"""
        sprite = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x * self.sprite_width, y * self.sprite_height, 
                                         self.sprite_width, self.sprite_height))
        return sprite
    
    def get_sprites(self, positions):
        """Get multiple sprites"""
        return [self.get_sprite(x, y) for x, y in positions]
    
    def get_row(self, row, count):
        """Get entire row of sprites"""
        return [self.get_sprite(i, row) for i in range(count)]