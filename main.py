import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

def launch_admin():
    """Launches the admin GUI."""
    try:
        # Get the absolute path to the admin script
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin', 'admin.py')

        # Launch the admin script using the same Python interpreter
        subprocess.Popen([sys.executable, script_path])

        # Optional: Close the main launcher window after launching the admin GUI
        # window.destroy()

    except FileNotFoundError:
        messagebox.showerror("Error", "Admin script not found. Make sure 'admin/admin.py' exists.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def launch_user():
    """Launches the user GUI."""
    try:
        # Get the absolute path to the user script
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user', 'user.py')

        # Launch the user script using the same Python interpreter
        subprocess.Popen([sys.executable, script_path])

        # Optional: Close the main launcher window after launching the user GUI
        # window.destroy()

    except FileNotFoundError:
        messagebox.showerror("Error", "User script not found. Make sure 'user/user.py' exists.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# --- Main Window Setup ---
window = tk.Tk()
window.title("App Launcher")
window.geometry("400x250")
window.resizable(False, False)

# --- Styling ---
BG_COLOR = "#f0f0f0"
BUTTON_BG_COLOR = "#4CAF50"
BUTTON_FG_COLOR = "white"
FONT_LARGE = ("Arial", 16, "bold")
FONT_MEDIUM = ("Arial", 12)

window.configure(bg=BG_COLOR)

# --- Widgets ---
main_frame = tk.Frame(window, bg=BG_COLOR, padx=20, pady=20)
main_frame.pack(expand=True, fill="both")

title_label = tk.Label(
    main_frame,
    text="Select an Interface to Launch",
    font=FONT_LARGE,
    bg=BG_COLOR
)
title_label.pack(pady=(0, 20))

admin_button = tk.Button(
    main_frame,
    text="Admin Interface",
    command=launch_admin,
    bg=BUTTON_BG_COLOR,
    fg=BUTTON_FG_COLOR,
    font=FONT_MEDIUM,
    width=20,
    height=2,
    relief="raised",
    borderwidth=2
)
admin_button.pack(pady=10)

user_button = tk.Button(
    main_frame,
    text="User Interface",
    command=launch_user,
    bg=BUTTON_BG_COLOR,
    fg=BUTTON_FG_COLOR,
    font=FONT_MEDIUM,
    width=20,
    height=2,
    relief="raised",
    borderwidth=2
)
user_button.pack(pady=10)

# --- Run the Application ---
if __name__ == "__main__":
    window.mainloop()
