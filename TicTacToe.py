import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self, master):
        self.master = master
        self.master.title("Tic Tac Toe")
        self.master.geometry("900x900")
        self.master.resizable(True, True)
        self.master.config(bg="blue")

        self.current_player = "X"
        self.board = [""] * 9

        self.create_board()

    def create_board(self):
        self.buttons = []
        button_size = 300  # Each button will be 300x300 pixels
        for i in range(3):
            for j in range(3):
                button = tk.Button(self.master, text="", font=("Helvetica", 100), width=4, height=2,
                                   bg="red", fg="white", command=lambda row=i, col=j: self.on_click(row, col))
                button.grid(row=i, column=j, sticky="nsew")
                self.buttons.append(button)

        # Configure grid to expand with window resizing
        for i in range(3):
            self.master.grid_rowconfigure(i, weight=1)
            self.master.grid_columnconfigure(i, weight=1)

    def on_click(self, row, col):
        index = 3 * row + col
        if self.board[index] == "":
            self.board[index] = self.current_player
            self.buttons[index].config(text=self.current_player)
            if self.check_winner():
                messagebox.showinfo("Game Over", f"Player {self.current_player} wins!")
                self.reset_game()
            elif "" not in self.board:
                messagebox.showinfo("Game Over", "It's a tie!")
                self.reset_game()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"

    def check_winner(self):
        win_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]
        for combo in win_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != "":
                return True
        return False

    def reset_game(self):
        self.current_player = "X"
        self.board = [""] * 9
        for button in self.buttons:
            button.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
