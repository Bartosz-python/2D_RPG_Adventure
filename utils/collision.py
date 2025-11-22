"""
src/utils/collision.py
Collision detection utilities
"""
import pygame

def check_collision_rect(rect1, rect2):
    """Check if two rectangles collide"""
    return rect1.colliderect(rect2)

def get_collision_normal(moving_rect, static_rect):
    """Get collision normal vector"""
    # Calculate overlap on each axis
    dx = moving_rect.centerx - static_rect.centerx
    dy = moving_rect.centery - static_rect.centery
    
    # Determine collision side
    if abs(dx) > abs(dy):
        return (1 if dx > 0 else -1, 0)
    else:
        return (0, 1 if dy > 0 else -1)

def point_in_rect(point, rect):
    """Check if point is inside rectangle"""
    return rect.collidepoint(point)

def rect_contains_point(rect, x, y):
    """Check if rectangle contains point"""
    return rect.left <= x <= rect.right and rect.top <= y <= rect.bottom

def get_overlapping_rects(rect, rect_list):
    """Get all rectangles overlapping with given rect"""
    return [r for r in rect_list if rect.colliderect(r)]

def resolve_collision(moving_rect, static_rect, velocity):
    """Resolve collision and return adjusted velocity"""
    vx, vy = velocity
    
    # Calculate overlap
    overlap_x = min(moving_rect.right - static_rect.left, static_rect.right - moving_rect.left)
    overlap_y = min(moving_rect.bottom - static_rect.top, static_rect.bottom - moving_rect.top)
    
    # Resolve on smallest overlap axis
    if overlap_x < overlap_y:
        if vx > 0:
            moving_rect.right = static_rect.left
        else:
            moving_rect.left = static_rect.right
        vx = 0
    else:
        if vy > 0:
            moving_rect.bottom = static_rect.top
        else:
            moving_rect.top = static_rect.bottom
        vy = 0
    
    return vx, vy