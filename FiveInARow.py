import tkinter as tk
from tkinter import messagebox

class FiveInARow:
    def __init__(self, master):
        self.master = master
        self.master.title("Five in a Row")
        self.master.geometry("1000x1000")
        self.master.resizable(False, False)
        self.master.config(bg="white")

        self.current_player = 1
        self.board = [[0 for _ in range(50)] for _ in range(50)]

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
            self.board[row][col] = self.current_player
            color = "blue" if self.current_player == 1 else "red"
            self.canvas.create_oval(col*20+2, row*20+2, (col+1)*20-2, (row+1)*20-2, fill=color, outline=color)

            if self.check_winner(row, col):
                messagebox.showinfo("Game Over", f"Player {self.current_player} wins!")
                self.reset_game()
            else:
                self.current_player = 3 - self.current_player  # Switch between 1 and 2

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
        self.canvas.delete("all")
        for i in range(51):
            self.canvas.create_line(i * 20, 0, i * 20, 1000, fill="gray")
            self.canvas.create_line(0, i * 20, 1000, i * 20, fill="gray")

if __name__ == "__main__":
    root = tk.Tk()
    game = FiveInARow(root)
    root.mainloop()
