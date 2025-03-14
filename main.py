#!/usr/bin/env python3
import sys
import traceback
import pygame
from ui_manager import UIManager
from game_logic import Game
from ai_opponent import AIPlayer

def main():
    try:
        # Initialize game logic
        game = Game()
        ai_player = AIPlayer('black')
        
        # Initialize UI Manager without parameters
        ui_manager = UIManager()
        
        # Run the UI manager to start the game loop
        ui_manager.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user. Exiting gracefully...")
    except Exception as e:
        print("An error occurred during startup:")
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()