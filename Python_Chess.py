import tkinter as tk
from PIL import Image, ImageTk
import chess
import chess.svg
import cairosvg

def evaluate_board(board):
    """Evaluate the board position using a simple material balance heuristic."""
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    score = 0
    for piece in piece_values:
        score += len(board.pieces(piece, chess.WHITE)) * piece_values[piece]
        score -= len(board.pieces(piece, chess.BLACK)) * piece_values[piece]
    return score


def minimax(board, depth, alpha, beta, maximizing_player):
    """Minimax with alpha-beta pruning."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def get_best_move(board, depth):
    """Find the best move for the current player."""
    best_move = None
    best_value = float('-inf') if board.turn else float('inf')
    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, float('-inf'), float('inf'), not board.turn)
        board.pop()
        if board.turn and board_value > best_value:  # Maximizing player
            best_value = board_value
            best_move = move
        elif not board.turn and board_value < best_value:  # Minimizing player
            best_value = board_value
            best_move = move
    return best_move


class ChessGUI:
    def __init__(self, root):
        self.board = chess.Board()
        self.root = root
        self.root.title("Chess AI")
        self.canvas = tk.Canvas(root, width=400, height=400)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)  # Binds left mouse click
        self.selected_square = None
        self.root.focus_set()
        self.update_board()

    def update_board(self):
        """Render the current board position on the canvas."""
        svg_board = chess.svg.board(board=self.board)

        with open("board.svg", "w") as f:
            f.write(svg_board)

        cairosvg.svg2png(url="board.svg", write_to="board.png")

        img = Image.open("board.png")
        tk_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=tk_img)
        self.canvas.image = tk_img

    def on_click(self, event):
        """Handle user clicks to select and make moves."""
        square_size = 400 // 8
        col = event.x // square_size
        row = 7 - (event.y // square_size)
        clicked_square = chess.square(col, row)

        print(f"Clicked on square: {chess.square_name(clicked_square)}")

        if self.selected_square is None:
            # First click: select a piece
            if self.board.piece_at(clicked_square) and self.board.piece_at(clicked_square).color == chess.WHITE:
                self.selected_square = clicked_square
                print(f"Selected square: {chess.square_name(self.selected_square)}")
                self.update_board()
        else:
            # Second click: attempt to move
            move = chess.Move(self.selected_square, clicked_square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                self.update_board()
                self.play_ai_turn()
            else:
                print("Invalid move!")
                self.selected_square = None
                self.update_board()

    def play_ai_turn(self):
        """Make the AI play its turn."""
        if not self.board.is_game_over():
            move = get_best_move(self.board, depth=3) 
            if move:
                self.board.push(move)
            self.update_board()
        else:
            self.show_game_over()

    def show_game_over(self):
        """Display the game-over state."""
        result = self.board.result()
        tk.messagebox.showinfo("Game Over", f"Game Over! Result: {result}")

def main():
    root = tk.Tk()
    ChessGUI(root)
    root.mainloop()


main()
