#!/usr/bin/env python3
"""
Bug Fix and Feature Improvement Description:

- Fixed the board orientation so that White is displayed at the bottom and Black at the top.
  • Updated mouse event handling to translate screen coordinates to board coordinates with a vertical flip.
  • Updated board rendering (draw_board and draw_pieces) to draw rows in reversed order.
  
- Changed the dark square color to a light brown (using LIGHT_BROWN) as requested.

- Implemented the feature to represent chess pieces using PNG images from the assets folder.
  • Added the load_images() method that loads and scales images based on a naming convention (e.g. assets/white_king.png).
  • Updated draw_piece_at() and draw_dragging_piece() methods to render the images.

- Maintained and improved drag-and-drop functionality so that the piece being dragged is highlighted.
  
- Made Black pieces AI-controlled:
  • Imported the AIPlayer from ai_opponent.py.
  • Created an AIPlayer instance for Black in UIManager.
  • Added execute_ai_move() in the game loop to let the AI automatically select and move Black pieces once its turn starts.
  • Disabled user interaction for black pieces so that only white pieces are draggable.
  
- Kept backward compatibility with game_logic.py and ai_opponent.py.
  
- Additional improvements:
  • Added a short delay before the AI move to simulate "thinking" time and let the user see the board update.
  
Run the script to launch the game. White (user-controlled) can move their pieces via drag-and-drop, while Black pieces are moved automatically by the AI.
"""

import sys
import pygame
from game_logic import Game
from ai_opponent import AIPlayer

# Define some colors
WHITE = (255, 255, 255)
# Use a light brown color for dark squares instead of light gray
LIGHT_BROWN = (222, 184, 135)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
HIGHLIGHT = (50, 200, 50)

class UIManager:
    def __init__(self, width=640, height=640, rows=8, cols=8):
        pygame.init()
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.tile_size = width // cols
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.game = Game()
        self.font = pygame.font.SysFont(None, 36)
        self.images = {}
        self.load_images()
        
        # Drag and drop variables
        self.dragging = False
        self.selected_piece = None
        # start_cell stores the board coordinate (row, col) with row 0 at the bottom
        self.start_cell = None
        self.drag_offset = (0, 0)
        self.drag_pos = (0, 0)
        
        # Initialize the AI for black pieces
        self.ai_player = AIPlayer('black')
        
        # Game state
        self.game_over = False
        self.game_result = None
        self.winner = None
    
    def load_images(self):
        """
        Loads and scales chess piece images from the assets folder.
        Expected file naming convention: assets/<color>_<piece>.png
        Example: assets/white_king.png, assets/black_knight.png, etc.
        """
        piece_names = ['King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn']
        for color in ['white', 'black']:
            for piece in piece_names:
                filename = f"assets/{color}_{piece.lower()}.png"
                try:
                    image = pygame.image.load(filename)
                    image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                    self.images[(color, piece)] = image
                except pygame.error as e:
                    print(f"Error loading image {filename}: {e}")
        
    def run(self):
        running = True
        while running:
            self.handle_events()
            # Only allow drag-drop events if it's White's turn and game is not over
            if self.game.current_turn == 'black' and not self.dragging and not self.game_over:
                self.execute_ai_move()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # If game is over, only allow quit event and restart on mouse click
            if self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Restart the game if clicked anywhere on the end game screen
                    self.restart_game()
                continue
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Allow user input only if it's White's turn (user-controlled)
                    if self.game.current_turn != 'white':
                        continue
                    mx, my = event.pos
                    col = mx // self.tile_size
                    # Transform y coordinate: board row 0 at bottom
                    row_from_top = my // self.tile_size
                    row = self.rows - 1 - row_from_top
                    # Ensure indices are within board boundaries
                    if 0 <= row < self.rows and 0 <= col < self.cols:
                        piece = self.game.board.board[row][col]
                        if piece and piece.color == 'white':
                            self.dragging = True
                            self.selected_piece = piece
                            self.start_cell = (row, col)
                            cell_x = col * self.tile_size
                            # Recalculate cell_y from the flipped board: 
                            cell_y = (self.rows - 1 - row) * self.tile_size
                            self.drag_offset = (mx - cell_x, my - cell_y)
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.drag_pos = event.pos
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    mx, my = event.pos
                    end_col = mx // self.tile_size
                    end_row_from_top = my // self.tile_size
                    end_row = self.rows - 1 - end_row_from_top
                    # Attempt move if drop is within board bounds
                    if 0 <= end_row < self.rows and 0 <= end_col < self.cols:
                        end_cell = (end_row, end_col)
                        if self.start_cell != end_cell:
                            result = self.game.make_move(self.start_cell, end_cell)
                            if result in ["checkmate", "stalemate"]:
                                self.game_over = True
                                self.game_result = result
                                self.winner = 'white' if result == "checkmate" else None
                    self.dragging = False
                    self.selected_piece = None
                    self.start_cell = None

    def execute_ai_move(self):
        """
        Checks if it is AI's turn (black) and if so, gets the move from the AIPlayer
        and makes the move. A short delay is added to simulate thinking time.
        """
        # Only execute if it's black's turn and no dragging is occurring
        if self.game.current_turn == 'black':
            move = self.ai_player.select_move(self.game)
            if move:
                # Delay to let the player see the board before the AI move is executed.
                pygame.time.wait(500)
                result = self.game.make_move(*move)
                print(f"AI moves from {move[0]} to {move[1]}")
                if result in ["checkmate", "stalemate"]:
                    self.game_over = True
                    self.game_result = result
                    self.winner = 'black' if result == "checkmate" else None
            else:
                print("AI has no valid moves. The game is a stalemate.")
                self.game_over = True
                self.game_result = "stalemate"
                self.winner = None
    
    def render(self):
        self.screen.fill(BLACK)
        self.draw_board()
        self.draw_pieces()
        if self.dragging and self.selected_piece is not None:
            self.draw_dragging_piece()
            
        # Draw end game screen if game is over
        if self.game_over:
            self.draw_end_game_screen()

    def draw_board(self):
        # Draw the board so that row 0 is at the bottom of the screen.
        for row in range(self.rows):
            # Calculate y-coordinate on screen: reverse the row order.
            screen_y = (self.rows - 1 - row) * self.tile_size
            for col in range(self.cols):
                # Alternate colors: white and light brown
                if (row + col) % 2 == 0:
                    color = WHITE
                else:
                    color = LIGHT_BROWN
                rect = pygame.Rect(col * self.tile_size, screen_y, self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, color, rect)
                # Draw grid lines
                pygame.draw.rect(self.screen, DARK_GRAY, rect, 1)

    def draw_pieces(self):
        board_arr = self.game.board.board
        # Iterate through board coordinates: row 0 is bottom, row 7 is top.
        for row in range(self.rows):
            for col in range(self.cols):
                piece = board_arr[row][col]
                # Skip drawing the piece if it is currently being dragged.
                if self.dragging and self.start_cell == (row, col):
                    continue
                if piece:
                    # Calculate the screen position with board flipping.
                    pos = (col * self.tile_size, (self.rows - 1 - row) * self.tile_size)
                    self.draw_piece_at(piece, pos)

    def draw_piece_at(self, piece, pos):
        # Draw the piece using its corresponding image from the assets.
        image = self.images.get((piece.color, piece.__class__.__name__))
        if image:
            self.screen.blit(image, pos)
        else:
            # Fallback: Render the first letter if the image is missing.
            abbrev = piece.__class__.__name__[0]
            if piece.__class__.__name__ == "Knight":
                abbrev = "N"
            text_color = BLACK if piece.color == 'white' else DARK_GRAY
            text_surface = self.font.render(abbrev, True, text_color)
            text_rect = text_surface.get_rect(center=(pos[0] + self.tile_size // 2, pos[1] + self.tile_size // 2))
            self.screen.blit(text_surface, text_rect)

    def draw_dragging_piece(self):
        # Draw the dragging piece at the current mouse position with the proper offset and a highlight.
        if self.selected_piece:
            image = self.images.get((self.selected_piece.color, self.selected_piece.__class__.__name__))
            mx, my = self.drag_pos
            blit_pos = (mx - self.drag_offset[0], my - self.drag_offset[1])
            center = (blit_pos[0] + self.tile_size // 2, blit_pos[1] + self.tile_size // 2)
            # Draw a highlight circle behind the piece.
            pygame.draw.circle(self.screen, HIGHLIGHT, center, self.tile_size // 2 - 5)
            if image:
                self.screen.blit(image, blit_pos)
            else:
                # Fallback: Render the first letter if the image is missing.
                abbrev = self.selected_piece.__class__.__name__[0]
                if self.selected_piece.__class__.__name__ == "Knight":
                    abbrev = "N"
                text_color = BLACK if self.selected_piece.color == 'white' else DARK_GRAY
                text_surface = self.font.render(abbrev, True, text_color)
                text_rect = text_surface.get_rect(center=center)
                self.screen.blit(text_surface, text_rect)

    def draw_end_game_screen(self):
        """Draw the end game screen showing the game result."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        self.screen.blit(overlay, (0, 0))
        
        # Draw result text
        if self.game_result == "checkmate":
            title_text = f"{self.winner.capitalize()} Wins!"
            subtitle_text = "Checkmate"
        else:  # stalemate
            title_text = "Draw!"
            subtitle_text = "Stalemate"
            
        # Title text (larger)
        title_font = pygame.font.SysFont(None, 72)
        title_surface = title_font.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 2 - 40))
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle text (smaller)
        subtitle_font = pygame.font.SysFont(None, 36)
        subtitle_surface = subtitle_font.render(subtitle_text, True, WHITE)
        subtitle_rect = subtitle_surface.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Click to play again text
        restart_font = pygame.font.SysFont(None, 28)
        restart_surface = restart_font.render("Click anywhere to play again", True, WHITE)
        restart_rect = restart_surface.get_rect(center=(self.width // 2, self.height // 2 + 80))
        self.screen.blit(restart_surface, restart_rect)
        
    def restart_game(self):
        """Reset the game state to start a new game."""
        self.game = Game()
        self.dragging = False
        self.selected_piece = None
        self.start_cell = None
        self.game_over = False
        self.game_result = None
        self.winner = None

if __name__ == "__main__":
    ui = UIManager()
    ui.run()