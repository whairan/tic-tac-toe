import tkinter as tk
from tkinter import ttk
import math
import copy

CELL_COUNT = 3
BASE_SIZE = 420  # starting canvas size


class TicTacToe(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic Tac Toe")

        # Main layout: canvas on the left, controls on the right
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left = ttk.Frame(self, padding=8)
        self.left.grid(row=0, column=0, sticky="nsew")
        self.left.grid_columnconfigure(0, weight=1)
        self.left.grid_rowconfigure(0, weight=1)

        self.right = ttk.Frame(self, padding=12)
        self.right.grid(row=0, column=1, sticky="ns")

        # Canvas
        self.canvas = tk.Canvas(
            self.left,
            width=BASE_SIZE,
            height=BASE_SIZE,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Configure>", self.on_resize)

        # Game state
        self.board = [["" for _ in range(CELL_COUNT)] for _ in range(CELL_COUNT)]
        self.current_player = "X"
        self.moves = 0
        self.game_over = False
        self.scores = {"X": 0, "O": 0, "Ties": 0}

        # Mode state
        self.mode_var = tk.StringVar(value="2P")  # "2P" or "CPU"
        self.mark_var = tk.StringVar(value="X")   # player mark when CPU mode
        self.ai_player = None                     # set on new_game()

        # Theme-driven colors and prominent label styles
        style = ttk.Style()
        paper = style.lookup("TFrame", "background") or "white"
        ink = style.lookup("TLabel", "foreground") or "#111111"
        self.paper = paper
        self.ink = ink
        self.canvas.configure(bg=self.paper)

        # Bigger, bolder text for results and scores
        style.configure("Result.TLabel", font=("TkDefaultFont", 16, "bold"))
        style.configure("Big.TLabel", font=("TkDefaultFont", 12, "bold"))

        # Controls on the right
        self.build_sidebar()

        # Initial draw
        self.size = BASE_SIZE
        self.draw_grid()

    def build_sidebar(self):
        # Result banner
        result_box = ttk.LabelFrame(self.right, text="Result")
        result_box.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.result_label = ttk.Label(
            result_box, text="Playing", style="Result.TLabel", anchor="center"
        )
        self.result_label.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        # Heading
        ttk.Label(
            self.right, text="Player Options", font=("TkDefaultFont", 12, "bold")
        ).grid(row=1, column=0, sticky="w", pady=(0, 8))

        # Opponent selection
        opp_box = ttk.LabelFrame(self.right, text="Opponent")
        opp_box.grid(row=2, column=0, sticky="ew", pady=6)
        ttk.Radiobutton(opp_box, text="Two players", variable=self.mode_var, value="2P").grid(
            row=0, column=0, sticky="w", padx=8, pady=4
        )
        ttk.Radiobutton(opp_box, text="Computer", variable=self.mode_var, value="CPU").grid(
            row=1, column=0, sticky="w", padx=8, pady=4
        )

        # Choose your mark (used when CPU is opponent)
        mark_box = ttk.LabelFrame(self.right, text="Your mark (vs Computer)")
        mark_box.grid(row=3, column=0, sticky="ew", pady=6)
        ttk.Radiobutton(mark_box, text="Play as X", variable=self.mark_var, value="X").grid(
            row=0, column=0, sticky="w", padx=8, pady=4
        )
        ttk.Radiobutton(mark_box, text="Play as O", variable=self.mark_var, value="O").grid(
            row=1, column=0, sticky="w", padx=8, pady=4
        )

        # Info
        info_box = ttk.LabelFrame(self.right, text="Player info")
        info_box.grid(row=4, column=0, sticky="ew", pady=6)
        self.turn_label = ttk.Label(info_box, text=f"Turn: {self.current_player}", style="Big.TLabel")
        self.turn_label.grid(row=0, column=0, sticky="w", padx=8, pady=2)
        self.moves_label = ttk.Label(info_box, text=f"Moves: {self.moves}")
        self.moves_label.grid(row=1, column=0, sticky="w", padx=8, pady=2)
        self.status_label = ttk.Label(info_box, text="Status: Playing")
        self.status_label.grid(row=2, column=0, sticky="w", padx=8, pady=2)

        # Score
        score_box = ttk.LabelFrame(self.right, text="Score")
        score_box.grid(row=5, column=0, sticky="ew", pady=6)
        self.score_x = ttk.Label(score_box, text=f"X wins: {self.scores['X']}", style="Big.TLabel")
        self.score_o = ttk.Label(score_box, text=f"O wins: {self.scores['O']}", style="Big.TLabel")
        self.score_t = ttk.Label(score_box, text=f"Ties: {self.scores['Ties']}", style="Big.TLabel")
        self.score_x.grid(row=0, column=0, sticky="w", padx=8, pady=2)
        self.score_o.grid(row=1, column=0, sticky="w", padx=8, pady=2)
        self.score_t.grid(row=2, column=0, sticky="w", padx=8, pady=2)

        # Controls
        btn_box = ttk.Frame(self.right)
        btn_box.grid(row=6, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(btn_box, text="New game", command=self.new_game).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(btn_box, text="Reset scores", command=self.reset_scores).grid(
            row=0, column=1, sticky="ew"
        )
        btn_box.grid_columnconfigure(0, weight=1)
        btn_box.grid_columnconfigure(1, weight=1)

        help_txt = (
            "Tip: after changing opponent or your mark, click New game.\n"
            "Computer plays optimally."
        )
        ttk.Label(self.right, text=help_txt, wraplength=220, foreground="#555555").grid(
            row=7, column=0, sticky="w", pady=8
        )

    # Drawing helpers
    def draw_grid(self):
        self.canvas.delete("all")
        cell = self.size // CELL_COUNT
        for i in range(1, CELL_COUNT):
            self.canvas.create_line(0, i * cell, self.size, i * cell, width=3, fill=self.ink)
            self.canvas.create_line(i * cell, 0, i * cell, self.size, width=3, fill=self.ink)
        # Redraw existing marks
        for r in range(CELL_COUNT):
            for c in range(CELL_COUNT):
                mark = self.board[r][c]
                if mark == "X":
                    self.draw_x(r, c)
                elif mark == "O":
                    self.draw_o(r, c)

    def draw_x(self, row, col):
        cell = self.size // CELL_COUNT
        pad = max(6, cell // 8)
        x0 = col * cell + pad
        y0 = row * cell + pad
        x1 = (col + 1) * cell - pad
        y1 = (row + 1) * cell - pad
        self.canvas.create_line(x0, y0, x1, y1, width=4, fill=self.ink)
        self.canvas.create_line(x0, y1, x1, y0, width=4, fill=self.ink)

    def draw_o(self, row, col):
        cell = self.size // CELL_COUNT
        pad = max(6, cell // 8)
        x0 = col * cell + pad
        y0 = row * cell + pad
        x1 = (col + 1) * cell - pad
        y1 = (row + 1) * cell - pad
        self.canvas.create_oval(x0, y0, x1, y1, width=4, outline=self.ink)

    # Events
    def on_resize(self, event):
        new_side = min(event.width, event.height)
        if new_side < 60:
            return
        self.size = new_side
        self.canvas.config(width=new_side, height=new_side)
        self.draw_grid()

    def on_click(self, event):
        if self.game_over:
            return

        # If CPU mode, ignore clicks when it's AI's turn
        if self.mode_var.get() == "CPU" and self.current_player == self.ai_player:
            return

        cell = self.size // CELL_COUNT
        col = min(max(event.x // cell, 0), CELL_COUNT - 1)
        row = min(max(event.y // cell, 0), CELL_COUNT - 1)
        if self.board[row][col]:
            return

        finished = self.place_mark(row, col, self.current_player)
        if finished:
            return

        # If playing vs computer, let AI move after human
        # self.ai_take_turn_if_needed()
        if self.mode_var.get() == "CPU":
            self.after(400, self.ai_take_turn_if_needed)

    # Shared move handler
    def place_mark(self, row, col, player):
        """Place a mark, update UI and game state. Returns True if game finished."""
        self.board[row][col] = player
        if player == "X":
            self.draw_x(row, col)
        else:
            self.draw_o(row, col)

        self.moves += 1
        self.moves_label.config(text=f"Moves: {self.moves}")

        winner = self.check_winner(self.board)
        if winner:
            self.status_label.config(text=f"Status: {winner} wins")
            self.scores[winner] += 1
            self.update_scores()
            self.set_result(f"{winner} wins", accent="win")
            self.game_over = True
            return True

        if self.moves == CELL_COUNT * CELL_COUNT:
            self.status_label.config(text="Status: Tie")
            self.scores["Ties"] += 1
            self.update_scores()
            self.set_result("Tie", accent="tie")
            self.game_over = True
            return True

        # Switch turns
        self.current_player = "O" if self.current_player == "X" else "X"
        self.turn_label.config(text=f"Turn: {self.current_player}")
        return False

    def ai_take_turn_if_needed(self):
        """If CPU mode and it's AI's turn, compute and make the move."""
        if self.mode_var.get() != "CPU" or self.game_over:
            return
        if self.current_player != self.ai_player:
            return

        row, col = self.best_ai_move()
        if row is not None:
            self.place_mark(row, col, self.ai_player)

    def set_result(self, text, accent=None):
        """Update the big Result banner with optional accent color."""
        color = self.ink
        if accent == "win":
            color = "#2aa84a"  # readable green
        elif accent == "tie":
            color = "#777777"
        self.result_label.config(text=text, foreground=color)

    # Game logic
    def check_winner(self, board):
        b = board
        # rows and cols
        for i in range(CELL_COUNT):
            if b[i][0] and b[i].count(b[i][0]) == CELL_COUNT:
                return b[i][0]
            col = [b[0][i], b[1][i], b[2][i]]
            if col[0] and col.count(col[0]) == CELL_COUNT:
                return col[0]
        # diagonals
        d1 = [b[0][0], b[1][1], b[2][2]]
        if d1[0] and d1.count(d1[0]) == CELL_COUNT:
            return d1[0]
        d2 = [b[0][2], b[1][1], b[2][0]]
        if d2[0] and d2.count(d2[0]) == CELL_COUNT:
            return d2[0]
        return None

    def update_scores(self):
        self.score_x.config(text=f"X wins: {self.scores['X']}")
        self.score_o.config(text=f"O wins: {self.scores['O']}")
        self.score_t.config(text=f"Ties: {self.scores['Ties']}")

    def new_game(self):
        self.board = [["" for _ in range(CELL_COUNT)] for _ in range(CELL_COUNT)]
        self.moves = 0
        self.game_over = False

        mode = self.mode_var.get()
        if mode == "CPU":
            human = self.mark_var.get()
            self.ai_player = "O" if human == "X" else "X"
            self.current_player = "X"  # X always starts
        else:
            self.ai_player = None
            self.current_player = "X"

        # If CPU mode and human chose O, AI starts
        self.turn_label.config(text=f"Turn: {self.current_player}")
        self.moves_label.config(text=f"Moves: {self.moves}")
        self.status_label.config(text="Status: Playing")
        self.set_result("Playing")
        self.draw_grid()

        # Let AI open if needed
        self.after(100, self.ai_take_turn_if_needed)

    def reset_scores(self):
        self.scores = {"X": 0, "O": 0, "Ties": 0}
        self.update_scores()

    # ---------- AI (minimax) ----------
    def best_ai_move(self):
        """Return best (row, col) for the current board for self.ai_player."""
        best_score = -math.inf
        best_move = (None, None)
        for r, c in self.available_moves(self.board):
            b2 = copy.deepcopy(self.board)
            b2[r][c] = self.ai_player
            score = self.minimax(b2, self.next_mark(self.ai_player))
            if score > best_score:
                best_score = score
                best_move = (r, c)
        return best_move

    def minimax(self, board, player_to_move):
        winner = self.check_winner(board)
        if winner:
            if winner == self.ai_player:
                return 1
            else:
                return -1
        if not self.available_moves(board):
            return 0  # tie

        if player_to_move == self.ai_player:
            best = -math.inf
            for r, c in self.available_moves(board):
                b2 = copy.deepcopy(board)
                b2[r][c] = player_to_move
                val = self.minimax(b2, self.next_mark(player_to_move))
                best = max(best, val)
            return best
        else:
            best = math.inf
            for r, c in self.available_moves(board):
                b2 = copy.deepcopy(board)
                b2[r][c] = player_to_move
                val = self.minimax(b2, self.next_mark(player_to_move))
                best = min(best, val)
            return best

    @staticmethod
    def available_moves(board):
        out = []
        for r in range(CELL_COUNT):
            for c in range(CELL_COUNT):
                if not board[r][c]:
                    out.append((r, c))
        return out

    @staticmethod
    def next_mark(mark):
        return "O" if mark == "X" else "X"


if __name__ == "__main__":
    app = TicTacToe()
    app.mainloop()
