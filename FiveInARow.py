import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
import pickle
import time
import tensorflow as tf
from tensorflow import keras
import xml.etree.ElementTree as ET
import os

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

        self.learning_rate = 0.001
        self.discount_factor = 0.99
        self.epsilon = 0.1
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.batch_size = 32
        self.memory = []
        self.max_memory = 10000

        self.model = self.build_model()
        self.target_model = self.build_model()
        self.update_target_model()

        self.developer_monitor = False
        self.games_played = 0
        self.dev_window = None

        # Load or initialize permanent data
        self.permanent_data = self.load_permanent_data()

        self.create_welcome_menu()

    def build_model(self):
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(100,)),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(100)
        ])
        model.compile(optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
                      loss='mse')
        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

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

            self.epsilon_label = tk.Label(self.dev_window, text=f"Epsilon: {self.epsilon:.4f}")
            self.epsilon_label.pack(pady=10)

            self.self_play_label = tk.Label(self.dev_window, text=self.get_self_play_stats())
            self.self_play_label.pack(pady=10)

    def get_self_play_stats(self):
        total = self.permanent_data['self_play']['total_games']
        if total == 0:
            return "No self-play games yet"
        blue_wins = self.permanent_data['self_play']['blue_wins']
        red_wins = self.permanent_data['self_play']['red_wins']
        ties = self.permanent_data['self_play']['ties']
        blue_ratio = (blue_wins / total) * 100 if total > 0 else 0
        red_ratio = (red_wins / total) * 100 if total > 0 else 0
        tie_ratio = (ties / total) * 100 if total > 0 else 0
        return f"self-play: {total}, blue wins: {blue_wins}({blue_ratio:.1f}%), red wins: {red_wins}({red_ratio:.1f}%), ties: {ties}({tie_ratio:.1f}%)"

    def update_dev_window(self):
        if self.developer_monitor and self.dev_window:
            self.games_label.config(text=f"Games played: {self.games_played}")
            self.epsilon_label.config(text=f"Epsilon: {self.epsilon:.4f}")
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
                    self.permanent_data['self_play']['blue_wins'] += 1
                else:
                    self.permanent_data['self_play']['red_wins'] += 1
                self.permanent_data['self_play']['total_games'] += 1
            elif self.play_with_computer:
                if winner == "Blue":
                    self.permanent_data['one_player']['player_wins'] += 1
                else:
                    self.permanent_data['one_player']['computer_wins'] += 1
                self.permanent_data['one_player']['total_games'] += 1
            else:
                messagebox.showinfo("Game Over", f"{winner} wins!")
            self.reset_game()
        elif self.moves_count == 100:  # Check for a tie (10x10 board)
            if self.is_self_play:
                self.permanent_data['self_play']['ties'] += 1
                self.permanent_data['self_play']['total_games'] += 1
            elif self.play_with_computer:
                self.permanent_data['one_player']['ties'] += 1
                self.permanent_data['one_player']['total_games'] += 1
            else:
                messagebox.showinfo("Game Over", "It's a tie!")
            self.reset_game()
        else:
            self.current_player = 3 - self.current_player  # Switch between 1 and 2

    def computer_move(self):
        state = self.get_state()
        if random.random() < self.epsilon:
            empty_cells = [(r, c) for r in range(10) for c in range(10) if self.board[r][c] == 0]
            action = random.choice(empty_cells) if empty_cells else None
        else:
            q_values = self.model.predict(np.array([state]))[0]
            valid_actions = [(r, c) for r in range(10) for c in range(10) if self.board[r][c] == 0]
            action = max(valid_actions, key=lambda a: q_values[a[0]*10 + a[1]])
        
        if action:
            row, col = action
            self.make_move(row, col)
            new_state = self.get_state()
            reward = self.get_reward(new_state)
            self.remember(state, action, reward, new_state, self.check_winner(row, col) or self.moves_count == 100)
            self.replay()

    def get_state(self):
        return np.array(self.board).flatten()

    def get_reward(self, state):
        if self.check_winner_state(state.reshape((10, 10)), 2):  # Computer wins
            return 1
        elif self.check_winner_state(state.reshape((10, 10)), 1):  # Player wins
            return -1
        elif np.all(state != 0):  # Draw
            return 0.5
        else:
            return 0

    def check_winner_state(self, state, player):
        for row in range(10):
            for col in range(10):
                if state[row][col] == player:
                    if self.check_winner(row, col, state):
                        return True
        return False

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > self.max_memory:
            self.memory.pop(0)

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.discount_factor * np.amax(self.target_model.predict(np.array([next_state]))[0])
            target_f = self.model.predict(np.array([state]))
            target_f[0][action[0]*10 + action[1]] = target
            self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

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
        if self.is_self_play:
            self.games_played += 1  # Increment games_played only once for self-play
        if not self.is_self_play:
            self.create_welcome_menu()
        self.update_target_model()
        self.update_dev_window()
        self.save_permanent_data()

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
        num_games = 20  # Number of self-play games
        for game in range(num_games):
            self.reset_game()
            while True:
                state = self.get_state()
                if random.random() < self.epsilon:
                    empty_cells = [(r, c) for r in range(10) for c in range(10) if self.board[r][c] == 0]
                    action = random.choice(empty_cells) if empty_cells else None
                else:
                    q_values = self.model.predict(np.array([state]))[0]
                    valid_actions = [(r, c) for r in range(10) for c in range(10) if self.board[r][c] == 0]
                    action = max(valid_actions, key=lambda a: q_values[a[0]*10 + a[1]])
                
                if action:
                    row, col = action
                    self.make_move(row, col)
                    self.update_board()  # Update the board visually
                    self.master.update()  # Update the GUI

                    new_state = self.get_state()
                    reward = self.get_reward(new_state)
                    done = self.check_winner(row, col) or self.moves_count == 100
                    self.remember(state, action, reward, new_state, done)
                    self.replay()
                    
                    if done:
                        self.update_board()
                        self.master.update()
                        break
                else:
                    break

            self.update_dev_window()
            self.master.update()  # Update the GUI

            if game % 100 == 0:
                print(f"Completed {game} self-play games")
                self.model.save('dqn_model.h5')

        print("Self-play training completed")
        self.model.save('dqn_model.h5')
        self.is_self_play = False  # Reset this after self-play is done
        self.save_permanent_data()

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

    def load_permanent_data(self):
        if os.path.exists('permanent_data.xml'):
            tree = ET.parse('permanent_data.xml')
            root = tree.getroot()
            data = {
                'self_play': {
                    'total_games': int(root.find('self_play/total_games').text),
                    'blue_wins': int(root.find('self_play/blue_wins').text),
                    'red_wins': int(root.find('self_play/red_wins').text),
                    'ties': int(root.find('self_play/ties').text)
                },
                'one_player': {
                    'total_games': int(root.find('one_player/total_games').text),
                    'player_wins': int(root.find('one_player/player_wins').text),
                    'computer_wins': int(root.find('one_player/computer_wins').text),
                    'ties': int(root.find('one_player/ties').text)
                }
            }
        else:
            data = {
                'self_play': {'total_games': 0, 'blue_wins': 0, 'red_wins': 0, 'ties': 0},
                'one_player': {'total_games': 0, 'player_wins': 0, 'computer_wins': 0, 'ties': 0}
            }
        return data

    def save_permanent_data(self):
        root = ET.Element('data')
        
        self_play = ET.SubElement(root, 'self_play')
        ET.SubElement(self_play, 'total_games').text = str(self.permanent_data['self_play']['total_games'])
        ET.SubElement(self_play, 'blue_wins').text = str(self.permanent_data['self_play']['blue_wins'])
        ET.SubElement(self_play, 'red_wins').text = str(self.permanent_data['self_play']['red_wins'])
        ET.SubElement(self_play, 'ties').text = str(self.permanent_data['self_play']['ties'])
        
        one_player = ET.SubElement(root, 'one_player')
        ET.SubElement(one_player, 'total_games').text = str(self.permanent_data['one_player']['total_games'])
        ET.SubElement(one_player, 'player_wins').text = str(self.permanent_data['one_player']['player_wins'])
        ET.SubElement(one_player, 'computer_wins').text = str(self.permanent_data['one_player']['computer_wins'])
        ET.SubElement(one_player, 'ties').text = str(self.permanent_data['one_player']['ties'])
        
        tree = ET.ElementTree(root)
        tree.write('permanent_data.xml')

if __name__ == "__main__":
    root = tk.Tk()
    game = FiveInARow(root)
    root.mainloop()