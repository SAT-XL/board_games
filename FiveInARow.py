import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
import pickle
import time

class FiveInARow:
    def __init__(self, master):
        self.master = master
        self.master.title("Five in a Row")
        self.master.geometry("400x400")  # Adjusted for 10x10 board
        self.master.resizable(False, False)
        self.master.config(bg="white")

        self.current_player = 1
        self.board = [[0 for _ in range(10)] for _ in range(10)]  # Changed to 10x10
        self.play_with_computer = False
        self.moves_count = 0  # Add a counter for moves
        self.is_self_play = False  # Add a flag for self-play mode

        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1
        self.load_q_table()

        self.developer_monitor = False
        self.games_played = 0
        self.dev_window = None

        # Add counters for self-play statistics
        self.self_play_count = 0
        self.blue_wins = 0
        self.red_wins = 0
        self.ties = 0

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

        self_play_button = tk.Button(self.welcome_frame, text="Self-Play Mode", command=self.start_self_play)
        self_play_button.pack(pady=10)

        dev_mode_button = tk.Button(self.welcome_frame, text="Developer Monitor", command=self.toggle_developer_monitor)
        dev_mode_button.pack(pady=10)

    def toggle_developer_monitor(self):
        self.developer_monitor = not self.developer_monitor
        if self.developer_monitor:
            self.create_dev_window()
        else:
            if self.dev_window:
                self.dev_window.destroy()
                self.dev_window = None

    def create_dev_window(self):
        if not self.dev_window:
            self.dev_window = tk.Toplevel(self.master)
            self.dev_window.title("Developer Monitor")
            self.dev_window.geometry("400x250")

            self.games_label = tk.Label(self.dev_window, text=f"Games played: {self.games_played}")
            self.games_label.pack(pady=10)

            self.q_learning_label = tk.Label(self.dev_window, text=f"Q-table size: {len(self.q_table)}")
            self.q_learning_label.pack(pady=10)

            self.self_play_label = tk.Label(self.dev_window, text=self.get_self_play_stats())
            self.self_play_label.pack(pady=10)

    def get_self_play_stats(self):
        total = self.self_play_count
        if total == 0:
            return "No self-play games yet"
        blue_ratio = (self.blue_wins / total) * 100 if total > 0 else 0
        red_ratio = (self.red_wins / total) * 100 if total > 0 else 0
        tie_ratio = (self.ties / total) * 100 if total > 0 else 0
        return f"self-play: {total}, blue wins: {self.blue_wins}({blue_ratio:.1f}%), red wins: {self.red_wins}({red_ratio:.1f}%), ties: {self.ties}({tie_ratio:.1f}%)"

    def update_dev_window(self):
        if self.developer_monitor and self.dev_window:
            self.games_label.config(text=f"Games played: {self.games_played}")
            self.q_learning_label.config(text=f"Q-table size: {len(self.q_table)}")
            self.self_play_label.config(text=self.get_self_play_stats())

    def start_game_with_player(self):
        self.play_with_computer = False
        self.is_self_play = False
        self.welcome_frame.destroy()
        self.create_board()

    def start_game_with_computer(self):
        self.play_with_computer = True
        self.is_self_play = False
        self.welcome_frame.destroy()
        self.create_board()

    def start_self_play(self):
        self.is_self_play = True  # Set this to True when starting self-play
        self.welcome_frame.destroy()
        self.create_board()
        self.self_play()

    def create_board(self):
        self.canvas = tk.Canvas(self.master, width=400, height=400, bg="white")  # Adjusted for 10x10 board
        self.canvas.pack()

        # Draw grid lines
        for i in range(11):  # Changed to 11 for 10x10 grid
            self.canvas.create_line(i * 40, 0, i * 40, 400, fill="gray")  # Adjusted spacing
            self.canvas.create_line(0, i * 40, 400, i * 40, fill="gray")  # Adjusted spacing

        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        col = event.x // 40  # Adjusted for new cell size
        row = event.y // 40  # Adjusted for new cell size

        if self.board[row][col] == 0:
            self.make_move(row, col)

            if self.play_with_computer and self.current_player == 2:
                self.computer_move()

    def make_move(self, row, col):
        self.board[row][col] = self.current_player
        color = "blue" if self.current_player == 1 else "red"
        self.canvas.create_oval(col*40+2, row*40+2, (col+1)*40-2, (row+1)*40-2, fill=color, outline=color)  # Adjusted for new cell size
        self.moves_count += 1  # Increment the move counter

        if self.check_winner(row, col):
            winner = "Blue" if self.current_player == 1 else "Red"
            if self.is_self_play:
                if winner == "Blue":
                    self.blue_wins += 1
                else:
                    self.red_wins += 1
            else:
                messagebox.showinfo("Game Over", f"{winner} wins!")
            self.reset_game()
        elif self.moves_count == 100:  # Check for a tie (10x10 board)
            if self.is_self_play:
                self.ties += 1
            else:
                messagebox.showinfo("Game Over", "It's a tie!")
            self.reset_game()
        else:
            self.current_player = 3 - self.current_player  # Switch between 1 and 2

    def computer_move(self):
        state = self.get_state()
        if random.random() < self.epsilon:
            empty_cells = [(r, c) for r in range(10) for c in range(10) if self.board[r][c] == 0]  # Changed to 10x10
            action = random.choice(empty_cells) if empty_cells else None
        else:
            action = self.get_best_action(state)
        
        if action:
            row, col = action
            self.make_move(row, col)
            new_state = self.get_state()
            reward = self.get_reward(new_state)
            self.update_q_table(state, action, reward, new_state)

    def get_state(self):
        return tuple(tuple(row) for row in self.board)

    def get_best_action(self, state):
        best_action = None
        best_value = float('-inf')
        for row in range(10):  # Changed to 10x10
            for col in range(10):  # Changed to 10x10
                if self.board[row][col] == 0:
                    action = (row, col)
                    value = self.q_table.get((state, action), 0)
                    if value > best_value:
                        best_value = value
                        best_action = action
        return best_action

    def get_reward(self, state):
        if self.check_winner_state(state, 2):  # Computer wins
            return 1
        elif self.check_winner_state(state, 1):  # Player wins
            return -1
        elif all(self.board[r][c] != 0 for r in range(10) for c in range(10)):  # Draw
            return 0.5
        else:
            return 0

    def check_winner_state(self, state, player):
        for row in range(10):  # Changed to 10x10
            for col in range(10):  # Changed to 10x10
                if state[row][col] == player:
                    if self.check_winner(row, col, state):
                        return True
        return False

    def update_q_table(self, state, action, reward, new_state):
        old_value = self.q_table.get((state, action), 0)
        next_max = max([self.q_table.get((new_state, (r, c)), 0) for r in range(10) for c in range(10) if self.board[r][c] == 0], default=0)  # Changed to 10x10
        new_value = (1 - self.learning_rate) * old_value + self.learning_rate * (reward + self.discount_factor * next_max)
        self.q_table[(state, action)] = new_value
        self.update_dev_window()

    def load_q_table(self):
        try:
            with open('q_table.pkl', 'rb') as f:
                self.q_table = pickle.load(f)
        except FileNotFoundError:
            self.q_table = {}

    def save_q_table(self):
        with open('q_table.pkl', 'wb') as f:
            pickle.dump(self.q_table, f)

    def reset_game(self):
        self.current_player = 1
        self.board = [[0 for _ in range(10)] for _ in range(10)]  # Changed to 10x10
        self.moves_count = 0  # Reset the move counter
        self.canvas.delete("all")
        for i in range(11):  # Changed to 11 for 10x10 grid
            self.canvas.create_line(i * 40, 0, i * 40, 400, fill="gray")  # Adjusted spacing
            self.canvas.create_line(0, i * 40, 400, i * 40, fill="gray")  # Adjusted spacing
        if self.play_with_computer and not self.is_self_play:
            self.games_played += 1
        if not self.is_self_play:
            self.create_welcome_menu()
        self.save_q_table()
        self.update_dev_window()

    def check_winner(self, row, col, state=None):
        if state is None:
            state = self.board
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                r, c = row + i*dr, col + i*dc
                if 0 <= r < 10 and 0 <= c < 10 and state[r][c] == state[row][col]:  # Changed to 10x10
                    count += 1
                else:
                    break
            for i in range(1, 5):
                r, c = row - i*dr, col - i*dc
                if 0 <= r < 10 and 0 <= c < 10 and state[r][c] == state[row][col]:  # Changed to 10x10
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

    def self_play(self):
        num_games = 10000  # Number of self-play games
        for game in range(num_games):
            self.reset_game()
            self.self_play_count += 1  # Increment self-play count here, once per game
            while True:
                state = self.get_state()
                if random.random() < self.epsilon:
                    empty_cells = [(r, c) for r in range(10) for c in range(10) if self.board[r][c] == 0]
                    action = random.choice(empty_cells) if empty_cells else None
                else:
                    action = self.get_best_action(state)
                
                if action:
                    row, col = action
                    self.make_move(row, col)
                    self.update_board()  # Update the board visually
                    self.master.update()  # Update the GUI

                    new_state = self.get_state()
                    reward = self.get_reward(new_state)
                    self.update_q_table(state, action, reward, new_state)
                    
                    if self.check_winner(row, col) or self.moves_count == 100:
                        self.update_board()
                        self.master.update()
                        break
                else:
                    break

            self.games_played += 1
            self.update_dev_window()
            self.master.update()  # Update the GUI

            if game % 100 == 0:
                print(f"Completed {game} self-play games")
                self.save_q_table()

        print("Self-play training completed")
        self.save_q_table()
        self.is_self_play = False  # Reset this after self-play is done

    def update_board(self):
        self.canvas.delete("all")
        for i in range(11):
            self.canvas.create_line(i * 40, 0, i * 40, 400, fill="gray")
            self.canvas.create_line(0, i * 40, 400, i * 40, fill="gray")
        for row in range(10):
            for col in range(10):
                if self.board[row][col] == 1:
                    self.canvas.create_oval(col*40+2, row*40+2, (col+1)*40-2, (row+1)*40-2, fill="blue", outline="blue")
                elif self.board[row][col] == 2:
                    self.canvas.create_oval(col*40+2, row*40+2, (col+1)*40-2, (row+1)*40-2, fill="red", outline="red")

if __name__ == "__main__":
    root = tk.Tk()
    game = FiveInARow(root)
    root.mainloop()