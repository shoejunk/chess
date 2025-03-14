#!/usr/bin/env python3
"""
Improved chess_piece module implementing chess pieces with improved move validation,
including correct pawn movement and castling logic for the king that prevents moving
into check.
Note: This implementation expects the board argument to be either a dictionary mapping
position tuples (row, col) to Piece instances (or None if empty), a 2D list, or an object
with a "board" attribute that holds the 2D array. Additionally, if the board provides an
"is_square_under_attack" method, the king’s move will be further validated against moving
into or through check.
"""

class Piece:
    def __init__(self, position, color):
        self.position = position  # (row, col)
        self.color = color  # 'white' or 'black'

    def is_valid_move(self, board, new_position):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def update_position(self, new_position):
        self.position = new_position

    def _get_square(self, board, pos):
        row, col = pos
        # If board is an object with a 'board' attribute, use the underlying array.
        if hasattr(board, "board"):
            try:
                return board.board[row][col]
            except IndexError:
                return None
        # If board supports .get (like a dictionary), use that.
        elif hasattr(board, "get"):
            return board.get(pos)
        else:
            try:
                return board[row][col]
            except IndexError:
                return None

    def _is_path_clear(self, board, start, end):
        """
        Helper method to check that the path (excluding start and end) between start and end is clear.
        Assumes a straight line move (horizontal, vertical, or diagonal).
        """
        if board is None:
            return True

        x, y = start
        nx, ny = end
        dx = nx - x
        dy = ny - y
        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
        cur_x, cur_y = x + step_x, y + step_y
        while (cur_x, cur_y) != (nx, ny):
            if self._get_square(board, (cur_x, cur_y)) is not None:
                return False
            cur_x += step_x
            cur_y += step_y
        return True

class Pawn(Piece):
    def is_valid_move(self, board, new_position):
        row, col = self.position
        nrow, ncol = new_position

        if self.color == 'white':
            direction = 1
            starting_row = 1
        else:
            direction = -1
            starting_row = 6

        # Move forward one square if not blocked.
        if nrow == row + direction and ncol == col:
            if board is None or self._get_square(board, new_position) is None:
                return True

        # Move forward two squares on first move.
        if nrow == row + 2 * direction and ncol == col and row == starting_row:
            intermediate = (row + direction, col)
            if board is None or (self._get_square(board, intermediate) is None and 
                                 self._get_square(board, new_position) is None):
                return True

        # Capture diagonally.
        if nrow == row + direction and abs(ncol - col) == 1:
            if board is not None:
                target = self._get_square(board, new_position)
                if target is not None and target.color != self.color:
                    return True
            else:
                return True

        return False

class Rook(Piece):
    def __init__(self, position, color):
        super().__init__(position, color)
        self.has_moved = False

    def is_valid_move(self, board, new_position):
        x, y = self.position
        nx, ny = new_position
        if x != nx and y != ny:
            return False
        if board is not None:
            if not self._is_path_clear(board, self.position, new_position):
                return False
            target = self._get_square(board, new_position)
            if target is not None and target.color == self.color:
                return False
        return True

class Knight(Piece):
    def is_valid_move(self, board, new_position):
        x, y = self.position
        nx, ny = new_position
        if (abs(x - nx), abs(y - ny)) in [(1, 2), (2, 1)]:
            if board is not None:
                target = self._get_square(board, new_position)
                if target is not None and target.color == self.color:
                    return False
            return True
        return False

class Bishop(Piece):
    def is_valid_move(self, board, new_position):
        x, y = self.position
        nx, ny = new_position
        if abs(x - nx) != abs(y - ny):
            return False
        if board is not None:
            if not self._is_path_clear(board, self.position, new_position):
                return False
            target = self._get_square(board, new_position)
            if target is not None and target.color == self.color:
                return False
        return True

class Queen(Piece):
    def is_valid_move(self, board, new_position):
        x, y = self.position
        nx, ny = new_position
        if (x == nx or y == ny) or (abs(x - nx) == abs(y - ny)):
            if board is not None:
                if not self._is_path_clear(board, self.position, new_position):
                    return False
                target = self._get_square(board, new_position)
                if target is not None and target.color == self.color:
                    return False
            return True
        return False

class King(Piece):
    def __init__(self, position, color):
        super().__init__(position, color)
        self.has_moved = False

    def is_valid_move(self, board, new_position):
        row, col = self.position
        nrow, ncol = new_position

        # Prevent moving to a square occupied by own piece.
        if board is not None:
            target = self._get_square(board, new_position)
            if target is not None and target.color == self.color:
                return False

        # Normal one-square move in any direction.
        if abs(nrow - row) <= 1 and abs(ncol - col) <= 1:
            if board is not None and hasattr(board, "is_square_under_attack"):
                print("DEBUG: Checking if square {} is under attack for King of color '{}'.".format(new_position, self.color))
                under_attack = board.is_square_under_attack(new_position, self.color)
                print("DEBUG: Result - square {} under attack: {}.".format(new_position, under_attack))
                if under_attack:
                    print("DEBUG: Move rejected. Destination {} is under attack.".format(new_position))
                    return False
            return True

        # Castling: King moves two squares horizontally on its first move.
        if nrow == row and abs(ncol - col) == 2 and not self.has_moved:
            if board is None:
                return True
            # Ensure the king is not currently in check.
            if hasattr(board, "is_square_under_attack"):
                print("DEBUG: Checking if king's current square {} is under attack.".format(self.position))
                current_attack = board.is_square_under_attack(self.position, self.color)
                print("DEBUG: Result - king's current square {} under attack: {}.".format(self.position, current_attack))
                if current_attack:
                    print("DEBUG: Castling rejected. King is currently in check at {}.".format(self.position))
                    return False
            # Kingside castling.
            if ncol > col:
                rook_position = (row, 7)
                rook = self._get_square(board, rook_position)
                if rook is None or rook.__class__.__name__ != "Rook" or getattr(rook, "has_moved", True):
                    return False
                intermediate = (row, col + 1)
                if self._get_square(board, intermediate) is not None:
                    return False
                if hasattr(board, "is_square_under_attack"):
                    for square in [(row, col + 1), (row, col + 2)]:
                        print("DEBUG: Checking if square {} is under attack during kingside castling for King of color '{}'.".format(square, self.color))
                        square_under_attack = board.is_square_under_attack(square, self.color)
                        print("DEBUG: Result - square {} under attack: {}.".format(square, square_under_attack))
                        if square_under_attack:
                            print("DEBUG: Castling rejected. Square {} is under attack.".format(square))
                            return False
                return True
            # Queenside castling.
            else:
                rook_position = (row, 0)
                rook = self._get_square(board, rook_position)
                if rook is None or rook.__class__.__name__ != "Rook" or getattr(rook, "has_moved", True):
                    return False
                # Check that the squares between king and rook are clear.
                intermediate1 = (row, col - 1)
                intermediate2 = (row, col - 2)
                if self._get_square(board, intermediate1) is not None or self._get_square(board, intermediate2) is not None:
                    return False
                # Optionally check the square adjacent to the rook (col - 3) if required.
                intermediate3 = (row, col - 3)
                if self._get_square(board, intermediate3) is not None:
                    return False
                if hasattr(board, "is_square_under_attack"):
                    for square in [(row, col - 1), (row, col - 2)]:
                        print("DEBUG: Checking if square {} is under attack during queenside castling for King of color '{}'.".format(square, self.color))
                        square_under_attack = board.is_square_under_attack(square, self.color)
                        print("DEBUG: Result - square {} under attack: {}.".format(square, square_under_attack))
                        if square_under_attack:
                            print("DEBUG: Castling rejected. Square {} is under attack.".format(square))
                            return False
                return True

        return False

# End of chess_piece module code.