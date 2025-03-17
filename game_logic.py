import pickle
from chess_board import Board
from chess_piece import King, Knight, Pawn

class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = 'white'
        self.move_history = []

    def switch_turn(self):
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

    def is_path_blocked(self, start, end):
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        if steps <= 1:
            return False
        step_x = dx // steps if dx != 0 else 0
        step_y = dy // steps if dy != 0 else 0
        current_x, current_y = x1 + step_x, y1 + step_y
        while (current_x, current_y) != (x2, y2):
            if self.board.board[current_x][current_y] is not None:
                return True
            current_x += step_x
            current_y += step_y
        return False

    def make_move(self, start, end):
        x, y = start
        piece = self.board.board[x][y]
        if piece is None:
            print(f"No piece at starting position {start}.")
            return False
        if piece.color != self.current_turn:
            print(f"It's {self.current_turn}'s turn. You cannot move a {piece.color} piece.")
            return False

        # Validate move with piece's own logic
        if not self.board.is_valid_move(piece, end):
            # Debug information for pawn moves
            if isinstance(piece, Pawn):
                debug_info = f"Attempting pawn move from {piece.position} to {end}. "
                x0, y0 = piece.position
                nx, ny = end
                if piece.color == 'white':
                    if nx == x0 + 1 and ny == y0:
                        debug_info += "One square forward move detected. "
                        if self.board.board[nx][ny] is not None:
                            debug_info += "Destination not empty."
                    elif x0 == 1 and nx == x0 + 2 and ny == y0:
                        debug_info += "Two square forward move detected from initial position. "
                        if self.board.board[x0+1][y0] is not None:
                            debug_info += " Intermediate square not empty. "
                        if self.board.board[nx][ny] is not None:
                            debug_info += " Destination not empty."
                    elif nx == x0 + 1 and abs(ny - y0) == 1:
                        debug_info += "Diagonal capture move detected."
                    else:
                        debug_info += "Move does not match pawn rules."
                else:
                    if nx == x0 - 1 and ny == y0:
                        debug_info += "One square forward move detected. "
                        if self.board.board[nx][ny] is not None:
                            debug_info += "Destination not empty."
                    elif x0 == 6 and nx == x0 - 2 and ny == y0:
                        debug_info += "Two square forward move detected from initial position. "
                        if self.board.board[x0-1][y0] is not None:
                            debug_info += " Intermediate square not empty. "
                        if self.board.board[nx][ny] is not None:
                            debug_info += " Destination not empty."
                    elif nx == x0 - 1 and abs(ny - y0) == 1:
                        debug_info += "Diagonal capture move detected."
                    else:
                        debug_info += "Move does not match pawn rules."
                print("Debug:", debug_info)
            print(f"Invalid move from {start} to {end} for {piece.__class__.__name__}.")
            return False

        # For sliding pieces, ensure that the path is not blocked
        if piece.__class__.__name__ in ['Rook', 'Bishop', 'Queen']:
            if self.is_path_blocked(start, end):
                print(f"Path blocked for move from {start} to {end}.")
                return False

        if self.board.move_piece(start, end):
            self.move_history.append((start, end))
            print(f"Moved {piece.__class__.__name__} from {start} to {end}.")
            
            # Switch turns first to check opponent's status
            self.switch_turn()
            
            # Check for checkmate or stalemate
            if self.board.is_checkmate(self.current_turn):
                print(f"{self.current_turn.capitalize()} is in checkmate! {piece.color.capitalize()} wins!")
                return "checkmate"
            elif self.board.is_stalemate(self.current_turn):
                print(f"{self.current_turn.capitalize()} is in stalemate! The game is a draw.")
                return "stalemate"
            
            # Game continues
            return "continue"
        else:
            print(f"Failed to move piece from {start} to {end}.")
            return False

    def is_king_present(self, color):
        for row in self.board.board:
            for piece in row:
                if piece is not None and piece.__class__.__name__ == 'King' and piece.color == color:
                    return True
        return False

    def save_game(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        print(f"Game saved to {filename}.")

    @staticmethod
    def load_game(filename):
        with open(filename, 'rb') as f:
            game = pickle.load(f)
        print(f"Game loaded from {filename}.")
        return game

def main():
    game = Game()
    print("Initial Board:")
    game.board.print_board()
    print("\n")

    print("Attempting white pawn move from (1,2) to (2,2):")
    game.make_move((1, 2), (2, 2))
    game.board.print_board()
    print("\n")

    print("Attempting white pawn two-square move from (1,3) to (3,3):")
    game.make_move((1, 3), (3, 3))
    game.board.print_board()
    print("\n")

    game.save_game("saved_game.pkl")
    loaded_game = Game.load_game("saved_game.pkl")
    print("Loaded game board:")
    loaded_game.board.print_board()

if __name__ == "__main__":
    main()