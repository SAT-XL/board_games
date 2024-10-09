import tkinter as tk
from tkinter import messagebox
import random

class FiveInARow:
    def __init__(self, master):
        self.master = master
        self.master.title("Five in a Row")
        self.master.geometry("1000x1000")
        self.master.resizable(False, False)
        self.master.config(bg="white")

        self.current_player = 1
        self.board = [[0 for _ in range(50)] for _ in range(50)]
        self.play_with_computer = False
        self.moves_count = 0  # Add a counter for moves

        self.create_welcome_menu()

    def create_welcome_menu(self):
        self.welcome_frame = tk.Frame(self.master, bg="white")
        self.welcome_frame.pack(expand=True)

        title = tk.Label(self.welcome_frame, text="Welcome to Five In A Row", font=("Helvetica", 24), bg="white")
        title.pack(pady=20)

        play_with_computer = tk.Button(self.welcome_frame, text="1 Player", command=self.start_game_with_computer)
        play_with_computer.pack(pady=10)

        play_with_player = tk.Button(self.welcome_frame, text="2 Players", command=self.start_game_with_player)
        play_with_player.pack(pady=10)

    def start_game_with_player(self):
        self.play_with_computer = False
        self.welcome_frame.destroy()
        self.create_board()

    def start_game_with_computer(self):
        self.play_with_computer = True
        self.welcome_frame.destroy()
        self.create_board()

    def create_board(self):
        self.canvas = tk.Canvas(self.master, width=1000, height=1000, bg="white")
        self.canvas.pack()

        # Draw grid lines
        for i in range(51):
            self.canvas.create_line(i * 20, 0, i * 20, 1000, fill="gray")
            self.canvas.create_line(0, i * 20, 1000, i * 20, fill="gray")

        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        col = event.x // 20
        row = event.y // 20

        if self.board[row][col] == 0:
            self.make_move(row, col)

            if self.play_with_computer and self.current_player == 2:
                self.computer_move()

    def make_move(self, row, col):
        self.board[row][col] = self.current_player
        color = "blue" if self.current_player == 1 else "red"
        self.canvas.create_oval(col*20+2, row*20+2, (col+1)*20-2, (row+1)*20-2, fill=color, outline=color)
        self.moves_count += 1  # Increment the move counter

        if self.check_winner(row, col):
            winner = "Player 1" if self.current_player == 1 else ("Player 2" if not self.play_with_computer else "Computer")
            messagebox.showinfo("Game Over", f"{winner} wins!")
            self.reset_game()
        elif self.moves_count == 2500:  # Check for a tie (50x50 board)
            messagebox.showinfo("Game Over", "It's a tie!")
            self.reset_game()
        else:
            self.current_player = 3 - self.current_player  # Switch between 1 and 2

    def computer_move(self):
        best_move = self.find_best_move()
        if best_move:
            row, col = best_move
            self.make_move(row, col)
        else:
            empty_cells = [(r, c) for r in range(50) for c in range(50) if self.board[r][c] == 0]
            if empty_cells:
                row, col = random.choice(empty_cells)
                self.make_move(row, col)

    def find_best_move(self):
        # Check for winning move
        for row in range(50):
            for col in range(50):
                if self.board[row][col] == 0:
                    self.board[row][col] = 2
                    if self.check_winner(row, col):
                        self.board[row][col] = 0
                        return (row, col)
                    self.board[row][col] = 0

        # Check for blocking opponent's winning move
        for row in range(50):
            for col in range(50):
                if self.board[row][col] == 0:
                    self.board[row][col] = 1
                    if self.check_winner(row, col):
                        self.board[row][col] = 0
                        return (row, col)
                    self.board[row][col] = 0

        # Find the move that creates the longest line for the computer
        best_score = 0
        best_move = None
        for row in range(50):
            for col in range(50):
                if self.board[row][col] == 0:
                    score = self.evaluate_move(row, col, 2)
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)

        return best_move

    def evaluate_move(self, row, col, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        max_count = 0
        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                r, c = row + i*dr, col + i*dc
                if 0 <= r < 50 and 0 <= c < 50 and self.board[r][c] == player:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                r, c = row - i*dr, col - i*dc
                if 0 <= r < 50 and 0 <= c < 50 and self.board[r][c] == player:
                    count += 1
                else:
                    break
            max_count = max(max_count, count)
        return max_count

    def check_winner(self, row, col):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                r, c = row + i*dr, col + i*dc
                if 0 <= r < 50 and 0 <= c < 50 and self.board[r][c] == self.current_player:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                r, c = row - i*dr, col - i*dc
                if 0 <= r < 50 and 0 <= c < 50 and self.board[r][c] == self.current_player:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

    def reset_game(self):
        self.current_player = 1
        self.board = [[0 for _ in range(50)] for _ in range(50)]
        self.moves_count = 0  # Reset the move counter
        self.canvas.delete("all")
        for i in range(51):
            self.canvas.create_line(i * 20, 0, i * 20, 1000, fill="gray")
            self.canvas.create_line(0, i * 20, 1000, i * 20, fill="gray")
        self.create_welcome_menu()

if __name__ == "__main__":
    root = tk.Tk()
    game = FiveInARow(root)
    root.mainloop()
