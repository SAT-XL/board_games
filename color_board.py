import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import tkinter as tk
import random

class ColorChangeBoard:
    def __init__(self, master):
        self.master = master
        self.master.title("Color Change Board")
        self.canvas = tk.Canvas(self.master, width=800, height=800)
        self.canvas.pack()

        self.squares = []
        self.create_board()
        self.randomize_black_squares()

        self.canvas.bind("<Motion>", self.on_hover)
        self.canvas.bind("<Button-1>", self.on_click)

        print("Board created");

    def create_board(self):
        for row in range(10):
            for col in range(10):
                x1, y1 = col * 80, row * 80
                x2, y2 = x1 + 80, y1 + 80
                square = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black", width=3)
                self.squares.append(square)

    def randomize_black_squares(self):
        black_squares = random.sample(self.squares, k=random.randint(10, 20))
        for square in black_squares:
            self.canvas.itemconfig(square, fill="black")

    def on_hover(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        if item in self.squares:
            current_color = self.canvas.itemcget(item, "fill")
            if current_color != "black":
                self.canvas.itemconfig(item, fill="green")
            for square in self.squares:
                if square != item and self.canvas.itemcget(square, "fill") == "green":
                    original_color = "white" if self.canvas.itemcget(square, "fill") != "blue" else "blue"
                    self.canvas.itemconfig(square, fill=original_color)

    def on_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        if item in self.squares:
            current_color = self.canvas.itemcget(item, "fill")
            if current_color == "white":
                self.canvas.itemconfig(item, fill="blue")
            elif current_color == "blue":
                self.canvas.itemconfig(item, fill="white")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorChangeBoard(root)
    root.mainloop()
