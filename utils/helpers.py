"""
src/utils/helpers.py
General helper functions
"""
import pygame
import math

def distance(pos1, pos2):
    """Calculate distance between two points"""
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return math.sqrt(dx**2 + dy**2)

def lerp(start, end, t):
    """Linear interpolation"""
    return start + (end - start) * t

def clamp(value, min_val, max_val):
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))

def normalize_vector(x, y):
    """Normalize a 2D vector"""
    length = math.sqrt(x**2 + y**2)
    if length == 0:
        return 0, 0
    return x / length, y / length

def angle_to_vector(angle):
    """Convert angle to direction vector"""
    return math.cos(angle), math.sin(angle)

def vector_to_angle(x, y):
    """Convert direction vector to angle"""
    return math.atan2(y, x)

def draw_text(screen, text, pos, font, color=(255, 255, 255), center=False):
    """Helper to draw text"""
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=pos)
        screen.blit(text_surface, text_rect)
    else:
        screen.blit(text_surface, pos)

def draw_text_with_shadow(screen, text, pos, font, color=(255, 255, 255), shadow_color=(0, 0, 0)):
    """Draw text with shadow"""
    # Shadow
    shadow_surface = font.render(text, True, shadow_color)
    screen.blit(shadow_surface, (pos[0] + 2, pos[1] + 2))
    # Text
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

def ease_in_out(t):
    """Ease in/out interpolation"""
    return t * t * (3.0 - 2.0 * t)

def ease_in(t):
    """Ease in interpolation"""
    return t * t

def ease_out(t):
    """Ease out interpolation"""
    return 1.0 - (1.0 - t) * (1.0 - t)

def screen_shake(intensity, duration):
    """Generate screen shake offset"""
    import random
    offset_x = random.randint(-intensity, intensity)
    offset_y = random.randint(-intensity, intensity)
    return offset_x, offset_y

def rect_to_grid(rect, tile_size):
    """Convert rect to grid coordinates"""
    grid_x = rect.x // tile_size
    grid_y = rect.y // tile_size
    return grid_x, grid_y

def grid_to_rect(grid_x, grid_y, tile_size):
    """Convert grid coordinates to rect"""
    return pygame.Rect(grid_x * tile_size, grid_y * tile_size, tile_size, tile_size)

def wrap_text(text, font, max_width):
    """Wrap text to fit within max width"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def load_image_with_scale(path, scale=1.0):
    """Load image and scale it"""
    try:
        image = pygame.image.load(path).convert_alpha()
        if scale != 1.0:
            new_width = int(image.get_width() * scale)
            new_height = int(image.get_height() * scale)
            image = pygame.transform.scale(image, (new_width, new_height))
        return image
    except:
        return None

def create_gradient_surface(width, height, color1, color2, vertical=True):
    """Create a gradient surface"""
    surface = pygame.Surface((width, height))
    
    if vertical:
        for y in range(height):
            t = y / height
            r = int(color1[0] * (1 - t) + color2[0] * t)
            g = int(color1[1] * (1 - t) + color2[1] * t)
            b = int(color1[2] * (1 - t) + color2[2] * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    else:
        for x in range(width):
            t = x / width
            r = int(color1[0] * (1 - t) + color2[0] * t)
            g = int(color1[1] * (1 - t) + color2[1] * t)
            b = int(color1[2] * (1 - t) + color2[2] * t)
            pygame.draw.line(surface, (r, g, b), (x, 0), (x, height))
    
    return surface

def timer(duration, callback):
    """Simple timer class"""
    class Timer:
        def __init__(self, duration, callback):
            self.duration = duration
            self.callback = callback
            self.elapsed = 0
            self.active = True
        
        def update(self, dt):
            if not self.active:
                return
            
            self.elapsed += dt
            if self.elapsed >= self.duration:
                self.callback()
                self.active = False
        
        def reset(self):
            self.elapsed = 0
            self.active = True
    
    return Timer(duration, callback)