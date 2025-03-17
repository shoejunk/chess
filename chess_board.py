"""
Bug Fix Description:
- Fixed issue where players could make moves leaving their own king in check by adding validation to ensure the move doesn't result in the king being under attack.
- Addressed castling simulation during move validation to correctly check king safety by temporarily moving the rook alongside the king.
- Improved castling logic in move validation to handle rook movement during temporary board state simulation.

Review Comments Addressed:
- When a king is in check, players can only make moves that resolve the check. This is now enforced by simulating the move and checking if the king remains in check.
- Castling validation now correctly simulates rook movement to ensure king's new position isn't under attack due to incomplete board state during checks.

Other Improvements:
- Enhanced move validation logic to handle castling as a special case, ensuring both king and rook positions are updated during temporary checks.
- Added comprehensive comments to clarify the simulation and restoration process during move validation.
"""

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
        target_r, target_c = square
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is None or piece.color == color:
                    continue
                pr, pc = piece.position
                if (pr, pc) == (target_r, target_c):
                    continue
                if isinstance(piece, Pawn):
                    direction = 1 if piece.color == 'white' else -1
                    attack_squares = [(pr + direction, pc - 1), (pr + direction, pc + 1)]
                    if square in attack_squares:
                        return True
                elif isinstance(piece, Knight):
                    if (abs(pr - target_r), abs(pc - target_c)) in [(1, 2), (2, 1)]:
                        return True
                elif isinstance(piece, King):
                    if max(abs(pr - target_r), abs(pc - target_c)) == 1:
                        return True
                elif isinstance(piece, Rook):
                    if pr == target_r or pc == target_c:
                        if self._path_clear(piece.position, square):
                            return True
                elif isinstance(piece, Bishop):
                    if abs(pr - target_r) == abs(pc - target_c):
                        if self._path_clear(piece.position, square):
                            return True
                elif isinstance(piece, Queen):
                    if pr == target_r or pc == target_c or abs(pr - target_r) == abs(pc - target_c):
                        if self._path_clear(piece.position, square):
                            return True
        return False

    def is_valid_move(self, piece, new_position):
        if not piece.is_valid_move(self, new_position):
            return False

        original_x, original_y = piece.position
        new_x, new_y = new_position
        original_piece_new_pos = self.board[new_x][new_y]
        original_piece_old_pos = self.board[original_x][original_y]

        # Temporarily move the piece
        self.board[original_x][original_y] = None
        self.board[new_x][new_y] = piece
        piece.position = (new_x, new_y)

        # Handle castling simulation
        rook = None
        rook_original_pos = None
        if isinstance(piece, King) and abs(new_y - original_y) == 2:
            rook_col = 7 if new_y > original_y else 0
            new_rook_col = new_y - 1 if new_y > original_y else new_y + 1
            rook_original_pos = (original_x, rook_col)
            rook_new_pos = (original_x, new_rook_col)
            rook = self.board[original_x][rook_col]
            if isinstance(rook, Rook) and not rook.has_moved:
                self.board[original_x][rook_col] = None
                self.board[original_x][new_rook_col] = rook
                rook.position = rook_new_pos

        # Find the king of the same color
        king_pos = None
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if isinstance(p, King) and p.color == piece.color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        # Check if king is in check
        in_check = self.is_square_under_attack(king_pos, piece.color) if king_pos else False

        # Restore board state
        self.board[original_x][original_y] = original_piece_old_pos
        self.board[new_x][new_y] = original_piece_new_pos
        piece.position = (original_x, original_y)
        if rook:
            self.board[rook_original_pos[0]][rook_original_pos[1]] = rook
            self.board[rook_new_pos[0]][rook_new_pos[1]] = None
            rook.position = rook_original_pos

        return not in_check

    def move_piece(self, current_position, new_position):
        x, y = current_position
        piece = self.board[x][y]
        if piece and self.is_valid_move(piece, new_position):
            nx, ny = new_position
            self.board[nx][ny] = piece
            self.board[x][y] = None
            piece.update_position(new_position)
            
            # Handle castling: move the rook
            if isinstance(piece, King) and abs(ny - y) == 2:
                if ny > y:
                    rook_col = 7
                    new_rook_col = ny - 1
                else:
                    rook_col = 0
                    new_rook_col = ny + 1

                rook = self.board[x][rook_col]
                if isinstance(rook, Rook) and not rook.has_moved:
                    self.board[x][rook_col] = None
                    self.board[x][new_rook_col] = rook
                    rook.update_position((x, new_rook_col))
                    rook.has_moved = True

            if hasattr(piece, "has_moved"):
                piece.has_moved = True
            return True
        else:
            return False

    def is_king_in_check(self, color):
        """Check if the king of the given color is in check."""
        king_pos = None
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False  # No king found (shouldn't happen in a normal game)
        
        return self.is_square_under_attack(king_pos, color)
    
    def has_valid_moves(self, color):
        """Check if the given color has any valid moves."""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is None or piece.color != color:
                    continue
                
                # Try all possible target squares for this piece
                for tr in range(8):
                    for tc in range(8):
                        if self.is_valid_move(piece, (tr, tc)):
                            return True
        
        return False
    
    def is_checkmate(self, color):
        """Check if the given color is in checkmate."""
        # King must be in check and there must be no valid moves
        return self.is_king_in_check(color) and not self.has_valid_moves(color)
    
    def is_stalemate(self, color):
        """Check if the given color is in stalemate."""
        # King must not be in check and there must be no valid moves
        return not self.is_king_in_check(color) and not self.has_valid_moves(color)

    def print_board(self):
        for row in self.board:
            print(' '.join([type(piece).__name__[0] if piece else '.' for piece in row]))

def main():
    board = Board()
    print("Initial Board:")
    board.print_board()
    print("\n")

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