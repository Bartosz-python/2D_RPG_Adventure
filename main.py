"""
Wild Eldoria - Main Entry Point
"""
import pygame
import sys
from src.core.game import Game
from src.config.settings import *

def main():
    """Initialize and run the game"""
    pygame.init()
    
    # Create game window with resizable flag
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Wild Eldoria")
    
    # Initialize game
    game = Game(screen)
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    fullscreen = False
    
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Toggle fullscreen with F11
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            
            game.handle_event(event)
        
        # Update game state
        game.update(dt)
        
        # Render
        game.render(screen)
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()