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
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                game.screen = screen
                game.update_screen_size(event.w, event.h, is_fullscreen=False)
            elif event.type == pygame.KEYDOWN:
                # Toggle fullscreen with F11
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                    game.screen = screen  # Update game's screen reference
            
            # Handle title bar button clicks
            action = game.handle_event(event)
            if action == 'minimize':
                # Minimize window (using SDL)
                pygame.display.iconify()
            elif action == 'maximize':
                # Toggle fullscreen
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                game.screen = screen  # Update game's screen reference
                screen_width, screen_height = screen.get_size()
                game.update_screen_size(screen_width, screen_height, is_fullscreen=fullscreen)
            elif action == 'close' or action == 'quit':
                running = False
        
        # Update game state
        game.update(dt)
        
        # Render
        game.render(screen)
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()