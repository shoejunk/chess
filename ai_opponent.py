#!/usr/bin/env python3
from chess_board import Board
from chess_piece import Piece
from game_logic import Game
import random

class AIPlayer:
    def __init__(self, color):
        self.color = color
    
    def select_move(self, game):
        """
        Select the best move for the AI player.
        Currently uses a simple strategy of selecting a random valid move.
        Returns the selected move as a tuple of ((start_row, start_col), (end_row, end_col)) or None if no valid moves.
        """
        valid_moves = []
        # Find all pieces of the AI's color
        for row in range(8):
            for col in range(8):
                piece = game.board.board[row][col]
                if piece and piece.color == self.color:
                    # For each piece, find all valid moves
                    for end_row in range(8):
                        for end_col in range(8):
                            if game.board.is_valid_move(piece, (end_row, end_col)):
                                valid_moves.append(((row, col), (end_row, end_col)))
        
        # Return a random valid move or None if no valid moves
        if valid_moves:
            return random.choice(valid_moves)
        return None

    def generate_valid_moves(self, game):
        valid_moves = []
        for x, row in enumerate(game.board.board):
            for y, piece in enumerate(row):
                if piece and piece.color == self.color:
                    current_position = (x, y)
                    for nx in range(8):
                        for ny in range(8):
                            new_position = (nx, ny)
                            if game.board.is_valid_move(piece, new_position):
                                valid_moves.append((current_position, new_position))
        return valid_moves

def main():
    game = Game()
    ai_player = AIPlayer('black')

    # Using board.print_board() in place of the non-existent print_game_state method.
    game.board.print_board()
    print("\nStarting a game against AI.")

    while True:
        if game.current_turn == 'black':
            move = ai_player.select_move(game)
            if move:
                result = game.make_move(*move)
                print(f"AI moves from {move[0]} to {move[1]}")
                if result == "checkmate":
                    print("AI wins the game!")
                    break
            else:
                print("AI has no valid moves. Stalemate.")
                break
        else:
            # For demonstration, let's make a simple valid move for white.
            move = ((1, 4), (3, 4))  # Pawn forward move
            result = game.make_move(*move)
            print(f"Player moves from {move[0]} to {move[1]}")
            if result == "checkmate":
                print("Player wins the game!")
                break
        
        game.board.print_board()

if __name__ == "__main__":
    main()