# Pi Memory Game by Matt DiMauro
# Built in PyCharm a fun Tkinter game to showcase GUI and data skills for my portfolio!
# I wanted to create an interactive game that also ties into data analysis skills.

import tkinter as tk
from tkinter import messagebox
import os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import winsound

class PiGame:
    # Initialize the game window, set up the UI, and load saved scores
    # Set up the main window with a fixed size and a light blue background
    def __init__(self, root):
        self.root = root
        self.root.title("Pi Memory Game")
        self.root.geometry("400x600")
        self.root.configure(bg="#E6F0FA")

        # Lists to keep track of widgets for each screen
        self.main_menu_widgets = []
        self.practice_mode_widgets = []
        self.instructions_widgets = []
        self.real_game_widgets = []
        self.progress_widgets = []

        # A string of the first 500 digits of pi - note im willing to add more if ever needed!
        self.pi_digits = ("3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679 "
                          "8214808651328230664709384460955058223172535940812848111745028410270193852110555964462294885493038196 "
                          "4428810975665933446128475648233786783165271201909145648566923460348610454326648213393607260249141273 "
                          "7245870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094 "
                          "3305727036575959195309218611738193261179310511854807446237996274956735188575272489122793818301194912")
        self.pi_digits = self.pi_digits.replace(" ", "")  # Remove spaces for easier indexing

        # Game state variables
        self.user_input = ""  # Tracks the digits the player has entered
        self.game_active = True  # Controls whether the game is ongoing
        self.wrong_guesses = 0  # Counts mistakes in Real Game mode
        self.show_hint = False  # Toggles hint display in Practice Mode
        self.pi_display = None  # Reference to the label showing Pi digits
        self.current_mode = "menu"  # Tracks which screen/mode we're in

        # Load the all-time high score from a file
        self.high_score_file = "high_score.txt"
        if os.path.exists(self.high_score_file):
            with open(self.high_score_file, "r") as f:
                try:
                    self.high_score = int(f.read().strip())
                except ValueError:
                    self.high_score = 0  # Default to 0 if the file is corrupted
        else:
            self.high_score = 0

        # Load daily scores into a dictionary for progress tracking
        self.daily_scores_file = "daily_scores.txt"
        self.daily_scores = {}
        if os.path.exists(self.daily_scores_file):
            with open(self.daily_scores_file, "r") as f:
                for line in f:
                    try:
                        date, score = line.strip().split(":")
                        self.daily_scores[date] = int(score)
                    except ValueError:
                        continue  # Skip malformed lines
        print(f"Loaded daily scores: {self.daily_scores}")  # Debug to confirm loading

        # Start the game by showing the main menu
        self.create_main_menu()

    # Bind keyboard events to the pi_display widget for digit input - I want the user to be able to click the calculator or type digits
    def bind_keys(self):
        if self.pi_display:
            self.pi_display.unbind("<Key>")
            self.pi_display.bind("<Key>", self.key_press)
            self.pi_display.focus_set()
            self.root.update()
            self.root.update_idletasks()

    # Unbind keyboard events when leaving a game mode
    def unbind_keys(self):
        if self.pi_display:
            self.pi_display.unbind("<Key>")

    # Save the all-time high score to a file
    def save_high_score(self):
        with open(self.high_score_file, "w") as f:
            f.write(str(self.high_score))

    # Save daily scores to a file for persistence tracking purposes
    def save_daily_scores(self):
        with open(self.daily_scores_file, "w") as f:
            for date, score in self.daily_scores.items():
                f.write(f"{date}:{score}\n")
        print(f"Saved daily scores: {self.daily_scores}")

    # Sound effect to play a short buzzer sound
    def play_buzzer(self):
        winsound.Beep(400, 300)

    # Create the main menu screen with buttons to navigate to other modes
    def create_main_menu(self):
        self.clear_screen()  # Clear any existing widgets
        self.current_mode = "menu"

        # Title label for the game
        self.label = tk.Label(self.root, text="Pi Memory Game", font=("Arial", 20, "bold"), bg="#E6F0FA")
        self.label.pack(pady=20, anchor="center")
        self.main_menu_widgets.append(self.label)

        # Show the all-time high score
        self.score_label = tk.Label(self.root, text=f"All-Time High Score: {self.high_score}", font=("Arial", 12), bg="#E6F0FA")
        self.score_label.pack(pady=5, anchor="center")
        self.main_menu_widgets.append(self.score_label)

        # Buttons to navigate to different modes
        # How to Play - detailed instructions on how to play the game and how the gamemodes work
        self.how_to_play_button = tk.Button(self.root, text="How to Play", font=("Arial", 14), width=15, command=self.show_instructions, bg="#F5F5DC", fg="black", relief="raised")
        self.how_to_play_button.pack(pady=10)
        self.main_menu_widgets.append(self.how_to_play_button)

        # Practice Game - way to practice learning pi - mode tells you when you egt one wrong and displays next correct digits to promote learning (this method helped me learn so many digits)
        self.practice_button = tk.Button(self.root, text="Practice Game", font=("Arial", 14), width=15, command=self.start_practice, bg="#F5F5DC", fg="black", relief="raised")
        self.practice_button.pack(pady=10)
        self.main_menu_widgets.append(self.practice_button)

        # Real Game - mode to test yourself. Keep going until you get 3 wrong. Then it tells you the next digits so you can keep tyesting and improving
        self.real_game_button = tk.Button(self.root, text="Real Game", font=("Arial", 14), width=15, command=self.start_real_game, bg="#F5F5DC", fg="black", relief="raised")
        self.real_game_button.pack(pady=10)
        self.main_menu_widgets.append(self.real_game_button)

        # View Progress  - view your progress over time and have the ability to view your scores by day
        self.progress_button = tk.Button(self.root, text="View Progress", font=("Arial", 14), width=15, command=self.show_progress, bg="#F5F5DC", fg="black", relief="raised")
        self.progress_button.pack(pady=10)
        self.main_menu_widgets.append(self.progress_button)

        # Progress Graph - view a graph of progress over time for the data people like me who find it interesting
        self.graph_button = tk.Button(self.root, text="Progress Graph", font=("Arial", 14), width=15, command=self.show_progress_graph, bg="#F5F5DC", fg="black", relief="raised")
        self.graph_button.pack(pady=10)
        self.main_menu_widgets.append(self.graph_button)

    # Display the game instructions and some fun facts about Pi
    def show_instructions(self):
        self.clear_screen()
        self.current_mode = "menu"

        # Instructions text with rules and Pi facts
        instructions_text = (
            "Welcome to the Pi Memory Game! \n\n"
            "How it works:\n"
            "1. Practice Mode: This mode was made to help you learn PI! Go as far as you can and if you get stuck, an incorrect guess will show you the next 5 digits to keep you going.\n"
            "2. Real Game: Test your true memory and pi skills! You get 3 incorrect guesses before the game ends.\n"
            "3. You can type the digits or tap the on-screen buttons - note the sequence always starts with '3.'.\n"
            "4. Your score is determined on how many digits you guess correctly in a row.\n\n"
            "Cool Pi Facts:\n"
            "- The world record for memorizing Pi belongs to Rajveer Meena, who recited **70,000 digits** in 2015 while blindfolded.\n"
            "- Pi is irrational and infinite — it never repeats and never ends.\n"
            "- March 14 (3/14) is Pi Day - always try to celebrate by eating real pie 🥧.\n"
            "- Pi is often calculated using the Chudnovsky algorithm, a formula involving factorials and square roots.\n"
        )
        # Instructions label
        self.instructions_label = tk.Label(self.root, text=instructions_text, font=("Arial", 12), wraplength=350, justify="left", bg="#E6F0FA")
        self.instructions_label.pack(pady=20)
        self.instructions_widgets.append(self.instructions_label)

        # Adding a back to menu button
        self.back_button = tk.Button(self.root, text="Back to Menu", font=("Arial", 14), width=15, command=self.create_main_menu, bg="#F5F5DC", fg="black", relief="raised")
        self.back_button.pack(pady=10, anchor="center")
        self.instructions_widgets.append(self.back_button)

    # Show the player's daily progress with stats and an export option
    def show_progress(self):
        self.clear_screen()
        self.current_mode = "menu"

        # Title for the progress screen
        title = tk.Label(self.root, text="★ Your Pi Progress ★", font=("Arial", 16, "bold"), bg="#E6F0FA")
        title.pack(pady=10, anchor="center")
        self.progress_widgets.append(title)

        # Explanation of what the screen does
        blip = tk.Label(self.root, text="Here’s a dictionary to track your daily high scores!", font=("Arial", 10, "italic"), bg="#E6F0FA")
        blip.pack(pady=5, anchor="center")
        self.progress_widgets.append(blip)

        # Check if there are any scores to display
        if not self.daily_scores:
            no_data = tk.Label(self.root, text="No scores yet! Play to start tracking~", font=("Arial", 12), bg="#E6F0FA")
            no_data.pack(pady=20)
            self.progress_widgets.append(no_data)
        else:
            # Create a frame to hold the score entries
            scores_frame = tk.Frame(self.root, bg="#E6F0FA")
            scores_frame.pack(pady=10)
            self.progress_widgets.append(scores_frame)

            # Display each score entry sorted by date (newest first)
            for date, score in sorted(self.daily_scores.items(), reverse=True):
                entry = tk.Label(scores_frame, text=f"★ {date} : {score} digits ★", font=("Arial", 12), bg="lightpink", width=30, relief="ridge")
                entry.pack(pady=5)
                self.progress_widgets.append(entry)

            # Calculate and show some basic stats
            scores = list(self.daily_scores.values())
            avg_score = sum(scores) / len(scores) if scores else 0
            best_day = max(self.daily_scores.items(), key=lambda x: x[1], default=("N/A", 0))
            stats_label = tk.Label(self.root, text=f"Average Score: {avg_score:.1f} | Best Day: {best_day[0]} ({best_day[1]} digits)", font=("Arial", 10), bg="#E6F0FA")
            stats_label.pack(pady=5, anchor="center")
            self.progress_widgets.append(stats_label)

            # Add a button to export scores to CSV
            export_button = tk.Button(self.root, text="Export Scores", font=("Arial", 12), width=15, command=self.export_scores, bg="#F5F5DC", fg="black", relief="raised")
            export_button.pack(pady=5)
            self.progress_widgets.append(export_button)

        # Back button to return to the main menu
        back_button = tk.Button(self.root, text="Back to Menu", font=("Arial", 14), width=15, command=self.create_main_menu, bg="#F5F5DC", fg="black", relief="raised")
        back_button.pack(pady=10, anchor="center")
        self.progress_widgets.append(back_button)

    # Plot the player's daily scores over time using matplotlib
    def show_progress_graph(self):
        if not self.daily_scores:
            messagebox.showinfo("No Data", "No scores to plot yet! Play some games first.")
            return

        # Prepare data for plotting
        dates = sorted(self.daily_scores.keys())
        scores = [self.daily_scores[date] for date in dates]

        # Create a line plot with markers
        plt.figure(figsize=(9, 7))
        plt.plot(dates, scores, marker="o", color="#0000FF", linestyle="-", linewidth=2, markersize=8)
        # Add a label above each point
        for i, score in enumerate(scores):
            plt.text(dates[i], score + 1, str(score), ha='center', va='bottom', fontsize=12)
        plt.title("Pi Memory Game Progress Over Time", fontsize=14)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Score (Digits)", fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.show()

    # Export daily scores to a CSV file
    def export_scores(self):
        if not self.daily_scores:
            messagebox.showinfo("No Data", "No scores to export yet!")
            return

        # Convert the dictionary to a dataFrame and save as csv
        df = pd.DataFrame(list(self.daily_scores.items()), columns=["Date", "Score"])
        df.to_csv("scores_export.csv", index=False)
        # Print the absolute path so the user knows where the file is saved
        absolute_path = os.path.abspath("scores_export.csv")
        print(f"Exported scores to: {absolute_path}")
        messagebox.showinfo("Success", f"Scores exported to scores_export.csv!\nLocation: {absolute_path}")

    # Start practice mode where players can learn Pi digits with hints
    def start_practice(self):
        self.clear_screen()
        self.user_input = ""
        self.game_active = True
        self.show_hint = False
        self.current_mode = "practice"

        # Display the current digits (starts with "3.")
        self.pi_display = tk.Label(self.root, text="3.", font=("Arial", 24, "bold"), bg="#E6F0FA")
        self.pi_display.pack(pady=20, anchor="center")
        self.practice_mode_widgets.append(self.pi_display)

        # Initial instruction to get the player started
        self.feedback = tk.Label(self.root, text="Start with 1", font=("Arial", 12), bg="#E6F0FA")
        self.feedback.pack(pady=5)
        self.practice_mode_widgets.append(self.feedback)

        # Create a keypad for clicking digits
        self.keypad_frame = tk.Frame(self.root, bg="#E6F0FA")
        self.keypad_frame.pack(pady=10)
        self.practice_mode_widgets.append(self.keypad_frame)

        buttons = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("0", 3, 1)
        ]
        for (num, row, col) in buttons:
            btn = tk.Button(self.keypad_frame, text=num, font=("Arial", 18), width=5, height=2, command=lambda n=num: self.enter_digit(n, practice=True), bg="#F5F5DC", fg="black", relief="raised")
            btn.grid(row=row, column=col, padx=5, pady=5)

        # Restart button to reset the game
        self.restart_button = tk.Button(self.root, text="Restart", font=("Arial", 14), width=15, command=self.restart_practice, bg="#F5F5DC", fg="black", relief="raised")
        self.restart_button.pack(pady=10)
        self.practice_mode_widgets.append(self.restart_button)

        # Back button to return to the main menu
        self.back_button = tk.Button(self.root, text="Back to Menu", font=("Arial", 14), width=15, command=self.create_main_menu, bg="#F5F5DC", fg="black", relief="raised")
        self.back_button.pack(pady=10, anchor="center")
        self.practice_mode_widgets.append(self.back_button)

        self.bind_keys()

    # Start the real game mode where players get 3 incorrect guesses before the game is over
    def start_real_game(self):
        self.clear_screen()
        self.user_input = ""
        self.game_active = True
        self.wrong_guesses = 0
        self.current_mode = "real"

        # Display the current digits (starts with "3.")
        self.pi_display = tk.Label(self.root, text="3.", font=("Arial", 24, "bold"), bg="#E6F0FA")
        self.pi_display.pack(pady=20, anchor="center")
        self.real_game_widgets.append(self.pi_display)

        # Initial instruction to get the player started
        self.feedback = tk.Label(self.root, text="Start with 1 - 3 guesses left", font=("Arial", 12), bg="#E6F0FA")
        self.feedback.pack(pady=5)
        self.real_game_widgets.append(self.feedback)

        # Create a keypad for clicking digits
        self.keypad_frame = tk.Frame(self.root, bg="#E6F0FA")
        self.keypad_frame.pack(pady=10)
        self.real_game_widgets.append(self.keypad_frame)

        buttons = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("0", 3, 1)
        ]
        for (num, row, col) in buttons:
            btn = tk.Button(self.keypad_frame, text=num, font=("Arial", 18), width=5, height=2, command=lambda n=num: self.enter_digit(n, practice=False), bg="#F5F5DC", fg="black", relief="raised")
            btn.grid(row=row, column=col, padx=5, pady=5)

        # Back button to return to the main menu
        self.back_button = tk.Button(self.root, text="Back to Menu", font=("Arial", 14), width=15, command=self.create_main_menu, bg="#F5F5DC", fg="black", relief="raised")
        self.back_button.pack(pady=10, anchor="center")
        self.real_game_widgets.append(self.back_button)

        self.bind_keys()

    # Handle digit entry check if correct and update scores in real game mode
    def enter_digit(self, digit, practice=True):
        if not self.game_active and not practice:
            return  # Don't allow input if the game is over

        # Calculate the index of the next digit to check
        next_index = len(self.user_input) + 2

        # Check if the player has reached the end of the Pi digits
        # Prevent crash by returning cleanly
        if next_index >= len(self.pi_digits):
            self.pi_display.config(text="You reached the end!", fg="green")
            self.play_buzzer()
            self.game_active = False
            self.feedback.config(text="You got all 500 digits!")
            return

        # Update the display to show the last 6 digits for readability
        full_display = "3." + self.user_input
        if len(full_display) <= 6:
            display_text = full_display
        else:
            display_text = full_display[-6:]

        # Check if the entered digit is correct
        if digit == self.pi_digits[next_index]:
            self.user_input += digit
            if len(full_display) <= 5:
                display_text = "3." + self.user_input
            else:
                display_text = ("3." + self.user_input)[-6:]
            self.pi_display.config(text=display_text, fg="green")
            if practice:
                if self.show_hint:
                    self.feedback.config(text="Back to normal - keep going")
                    self.show_hint = False
                else:
                    self.feedback.config(text="Nice one! Keep going")
            else:
                self.feedback.config(text=f"Correct - {3 - self.wrong_guesses} guesses left")
        else:
            # In Practice Mode show the correct digit and the next 5 to help the player learn
            if practice:
                self.pi_display.config(text=display_text, fg="green")
                next_five = self.pi_digits[next_index:next_index + 5]
                self.feedback.config(text=f"Incorrect, the next number was {self.pi_digits[next_index]} - Next 5: {next_five}")
                self.show_hint = True
            # In Real Game mode count wrong guesses and end after 3
            else:
                self.play_buzzer() # sound effect
                self.wrong_guesses += 1
                if self.wrong_guesses < 3:
                    self.feedback.config(text=f"Wrong! {3 - self.wrong_guesses} guesses left - try again")
                    self.pi_display.config(text=display_text, fg="green")
                else:
                    self.play_buzzer() # sound effect
                    self.game_active = False
                    score = len(self.user_input)
                    today = datetime.now().strftime("%Y-%m-%d")
                    # Update daily scores if this is a new high for the day
                    if today not in self.daily_scores or score > self.daily_scores[today]:
                        self.daily_scores[today] = score
                        self.save_daily_scores()
                    # Update all-time high score if applicable
                    if score > self.high_score:
                        self.high_score = score
                        self.feedback.config(text=f"Game Over! New high score: {score}")
                        self.save_high_score()
                    else:
                        self.feedback.config(text=f"Game Over! Score: {score}")
                    # Show the next 10 digits for reference
                    next_ten = self.pi_digits[next_index:next_index + 10]
                    if self.root.winfo_exists():
                        messagebox.showinfo("Game Over", f"Next 10 digits: {next_ten}")

    # Handle keyboard input by routing to the correct mode
    def key_press(self, event):
        if event.char in "0123456789":
            if self.current_mode == "practice":
                self.enter_digit(event.char, practice=True)
            elif self.current_mode == "real":
                self.enter_digit(event.char, practice=False)

    # Reset Practice Mode to start over
    def restart_practice(self):
        self.user_input = ""
        self.game_active = True
        self.show_hint = False
        self.current_mode = "practice"
        self.pi_display.config(text="3.", fg="black")
        self.feedback.config(text="Start with 1")
        self.bind_keys()

    # Clear widgets from the screen to switch modes
    def clear_screen(self):
        self.unbind_keys()
        for widget in self.root.winfo_children():
            widget.pack_forget()
        self.pi_display = None

# Create a new Tkinter window and start the game
def run_game():
    root = tk.Tk()
    game = PiGame(root)
    root.mainloop()

if __name__ == "__main__":
    run_game()