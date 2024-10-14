import tkinter as tk
from tkinter import messagebox
import random

class FifteenPuzzle:
    def __init__(self, master):
        self.master = master
        self.master.title("15 Puzzle")
        self.master.geometry("400x450")
        self.master.resizable(False, False)

        self.board = list(range(1, 16)) + [0]  # 0 represents the empty tile
        self.solved_state = list(range(1, 16)) + [0]
        self.shuffle()

        self.buttons = []
        for i in range(4):
            for j in range(4):
                button = tk.Button(master, width=5, height=2, font=('Arial', 20, 'bold'),
                                   command=lambda row=i, col=j: self.click(row, col))
                button.grid(row=i, column=j, padx=2, pady=2)
                self.buttons.append(button)

        self.moves = 0
        self.moves_label = tk.Label(master, text="Moves: 0", font=('Arial', 12))
        self.moves_label.grid(row=4, column=0, columnspan=4, pady=10)

        self.new_game_button = tk.Button(master, text="New Game", command=self.new_game)
        self.new_game_button.grid(row=5, column=0, columnspan=4)

        self.update_board()

    def shuffle(self):
        random.shuffle(self.board)
        while not self.is_solvable():
            random.shuffle(self.board)

    def is_solvable(self):
        inversions = 0
        for i in range(len(self.board)):
            for j in range(i + 1, len(self.board)):
                if self.board[i] != 0 and self.board[j] != 0 and self.board[i] > self.board[j]:
                    inversions += 1
        return inversions % 2 == 0

    def update_board(self):
        for i, button in enumerate(self.buttons):
            if self.board[i] != 0:
                button.config(text=str(self.board[i]), state=tk.NORMAL)
            else:
                button.config(text="", state=tk.DISABLED)

    def click(self, row, col):
        index = 4 * row + col
        if self.is_valid_move(index):
            empty_index = self.board.index(0)
            self.board[empty_index], self.board[index] = self.board[index], self.board[empty_index]
            self.moves += 1
            self.moves_label.config(text=f"Moves: {self.moves}")
            self.update_board()
            if self.board == self.solved_state:
                messagebox.showinfo("Congratulations!", f"You solved the puzzle in {self.moves} moves!")

    def is_valid_move(self, index):
        empty_index = self.board.index(0)
        return (index // 4 == empty_index // 4 and abs(index % 4 - empty_index % 4) == 1) or \
               (index % 4 == empty_index % 4 and abs(index // 4 - empty_index // 4) == 1)

    def new_game(self):
        self.board = list(range(1, 16)) + [0]
        self.shuffle()
        self.moves = 0
        self.moves_label.config(text="Moves: 0")
        self.update_board()

if __name__ == "__main__":
    root = tk.Tk()
    game = FifteenPuzzle(root)
    root.mainloop()
