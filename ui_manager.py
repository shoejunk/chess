#!/usr/bin/env python3
"""
Bug Fix and Feature Improvement Description:
- Fixed the board rendering to use a light brown color for the dark squares instead of light gray.
- Implemented the requested feature of using PNG images from the assets folder to represent chess pieces instead of text abbreviations.
    • Added a load_images() method inside the UIManager class that loads and scales the chess piece images.
    • Updated draw_piece_at() and draw_dragging_piece() methods to render images from the loaded dictionary.
- Maintained the drag-and-drop functionality and ensured that the image representation of pieces is responsive.
- Kept backward compatibility with existing game_logic.py and ai_opponent.py files.
"""

import sys
import pygame
from game_logic import Game

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
        self.start_cell = None
        self.drag_offset = (0, 0)
        self.drag_pos = (0, 0)
        
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
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    col = mx // self.tile_size
                    row = my // self.tile_size
                    # Ensure indices are within board boundaries
                    if 0 <= row < self.rows and 0 <= col < self.cols:
                        piece = self.game.board.board[row][col]
                        if piece and piece.color == self.game.current_turn:
                            self.dragging = True
                            self.selected_piece = piece
                            self.start_cell = (row, col)
                            cell_x = col * self.tile_size
                            cell_y = row * self.tile_size
                            self.drag_offset = (mx - cell_x, my - cell_y)
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.drag_pos = event.pos
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    mx, my = event.pos
                    end_col = mx // self.tile_size
                    end_row = my // self.tile_size
                    # Attempt move if drop is within board bounds
                    if 0 <= end_row < self.rows and 0 <= end_col < self.cols:
                        end_cell = (end_row, end_col)
                        if self.start_cell != end_cell:
                            self.game.make_move(self.start_cell, end_cell)
                    self.dragging = False
                    self.selected_piece = None
                    self.start_cell = None

    def render(self):
        self.screen.fill(BLACK)
        self.draw_board()
        self.draw_pieces()
        if self.dragging and self.selected_piece is not None:
            self.draw_dragging_piece()

    def draw_board(self):
        for row in range(self.rows):
            for col in range(self.cols):
                # Alternate colors: white and light brown
                if (row + col) % 2 == 0:
                    color = WHITE
                else:
                    color = LIGHT_BROWN
                rect = pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, color, rect)
                # Draw grid lines
                pygame.draw.rect(self.screen, DARK_GRAY, rect, 1)

    def draw_pieces(self):
        board_arr = self.game.board.board
        for row in range(self.rows):
            for col in range(self.cols):
                piece = board_arr[row][col]
                # Skip drawing the piece if it is currently being dragged
                if self.dragging and self.start_cell == (row, col):
                    continue
                if piece:
                    self.draw_piece_at(piece, (col * self.tile_size, row * self.tile_size))

    def draw_piece_at(self, piece, pos):
        # Draw the piece using its corresponding image from the assets
        image = self.images.get((piece.color, piece.__class__.__name__))
        if image:
            self.screen.blit(image, pos)
        else:
            # Fallback: Render the first letter if the image is missing
            abbrev = piece.__class__.__name__[0]
            if piece.__class__.__name__ == "Knight":
                abbrev = "N"
            color = BLACK if piece.color == 'white' else DARK_GRAY
            text_surface = self.font.render(abbrev, True, color)
            text_rect = text_surface.get_rect(center=(pos[0] + self.tile_size // 2, pos[1] + self.tile_size // 2))
            self.screen.blit(text_surface, text_rect)

    def draw_dragging_piece(self):
        # Draw the dragging piece at the current mouse position offset properly with a highlight
        if self.selected_piece:
            image = self.images.get((self.selected_piece.color, self.selected_piece.__class__.__name__))
            mx, my = self.drag_pos
            blit_pos = (mx - self.drag_offset[0], my - self.drag_offset[1])
            center = (blit_pos[0] + self.tile_size // 2, blit_pos[1] + self.tile_size // 2)
            # Draw a highlight circle behind the piece
            pygame.draw.circle(self.screen, HIGHLIGHT, center, self.tile_size // 2 - 5)
            if image:
                self.screen.blit(image, blit_pos)
            else:
                # Fallback: Render the first letter if the image is missing
                abbrev = self.selected_piece.__class__.__name__[0]
                if self.selected_piece.__class__.__name__ == "Knight":
                    abbrev = "N"
                color = BLACK if self.selected_piece.color == 'white' else DARK_GRAY
                text_surface = self.font.render(abbrev, True, color)
                text_rect = text_surface.get_rect(center=center)
                self.screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    ui = UIManager()
    ui.run()