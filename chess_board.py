#!/usr/bin/env python3
from chess_piece import Pawn, Rook, Knight, Bishop, Queen, King

class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_pieces()

    def setup_pieces(self):
        # Set up pawns
        for i in range(8):
            self.board[1][i] = Pawn((1, i), 'white')
            self.board[6][i] = Pawn((6, i), 'black')

        # Set up other pieces
        placement = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, Piece in enumerate(placement):
            self.board[0][i] = Piece((0, i), 'white')
            self.board[7][i] = Piece((7, i), 'black')

    def _path_clear(self, start, end):
        (r, c) = start
        (r2, c2) = end
        dr = 0 if r2 == r else (1 if r2 > r else -1)
        dc = 0 if c2 == c else (1 if c2 > c else -1)
        current_r, current_c = r + dr, c + dc
        while (current_r, current_c) != (r2, c2):
            if self.board[current_r][current_c] is not None:
                return False
            current_r += dr
            current_c += dc
        return True

    def is_square_under_attack(self, square, color):
        print("DEBUG: Called is_square_under_attack with square {} for color '{}'".format(square, color))
        target_r, target_c = square
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is None or piece.color == color:
                    continue
                pr, pc = piece.position
                # Skip checking the enemy piece that occupies the square itself.
                if (pr, pc) == (target_r, target_c):
                    continue
                # Pawn attack: Pawns capture diagonally.
                if isinstance(piece, Pawn):
                    direction = 1 if piece.color == 'white' else -1
                    attack_squares = [(pr + direction, pc - 1), (pr + direction, pc + 1)]
                    if square in attack_squares:
                        print("DEBUG: Square {} is under attack by Pawn at {}".format(square, piece.position))
                        return True
                # Knight attack.
                elif isinstance(piece, Knight):
                    if (abs(pr - target_r), abs(pc - target_c)) in [(1, 2), (2, 1)]:
                        print("DEBUG: Square {} is under attack by Knight at {}".format(square, piece.position))
                        return True
                # King attack.
                elif isinstance(piece, King):
                    if max(abs(pr - target_r), abs(pc - target_c)) == 1:
                        print("DEBUG: Square {} is under attack by King at {}".format(square, piece.position))
                        return True
                # Rook attack.
                elif isinstance(piece, Rook):
                    if pr == target_r or pc == target_c:
                        if self._path_clear(piece.position, square):
                            print("DEBUG: Square {} is under attack by Rook at {}".format(square, piece.position))
                            return True
                # Bishop attack.
                elif isinstance(piece, Bishop):
                    if abs(pr - target_r) == abs(pc - target_c):
                        if self._path_clear(piece.position, square):
                            print("DEBUG: Square {} is under attack by Bishop at {}".format(square, piece.position))
                            return True
                # Queen attack.
                elif isinstance(piece, Queen):
                    if pr == target_r or pc == target_c or abs(pr - target_r) == abs(pc - target_c):
                        if self._path_clear(piece.position, square):
                            print("DEBUG: Square {} is under attack by Queen at {}".format(square, piece.position))
                            return True
        print("DEBUG: Square {} is not under attack for '{}'".format(square, color))
        return False

    def is_valid_move(self, piece, new_position):
        if not piece.is_valid_move(self, new_position):
            return False
        # Additional rules such as checks or pins can be added here.
        return True

    def move_piece(self, current_position, new_position):
        x, y = current_position
        piece = self.board[x][y]
        if piece and self.is_valid_move(piece, new_position):
            nx, ny = new_position
            self.board[nx][ny] = piece
            self.board[x][y] = None
            piece.update_position(new_position)
            if hasattr(piece, "has_moved"):
                piece.has_moved = True
            return True
        else:
            print("Invalid move from {} to {}".format(current_position, new_position))
            return False

    def print_board(self):
        for row in self.board:
            print(' '.join([type(piece).__name__[0] if piece else '.' for piece in row]))

def main():
    # Step 1: Initialize a board and print it
    board = Board()
    print("Initial Board:")
    board.print_board()
    print("\n")

    # Step 2: Execute a series of moves (some valid, some invalid)
    moves = [((1, 1), (3, 1)), ((6, 0), (5, 0)), ((0, 1), (2, 2))]
    for current, new in moves:
        if board.move_piece(current, new):
            print("Moved piece from {} to {}".format(current, new))
        else:
            print("Invalid move from {} to {}".format(current, new))
        board.print_board()
        print()

if __name__ == '__main__':
    main()