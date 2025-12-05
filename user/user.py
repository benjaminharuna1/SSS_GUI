import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3
import os

# --- Database Setup ---
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'songs.db')

def get_db_connection():
    """Establishes and returns a database connection."""
    if not os.path.exists(DB_PATH):
        messagebox.showerror("Database Error", "The song database was not found.")
        return None
    return sqlite3.connect(DB_PATH)

# --- User Application ---
class UserApp:
    def __init__(self, window):
        self.window = window
        self.window.title("User Interface - Song Viewer")
        self.window.geometry("900x700")

        self.create_widgets()
        self.load_songs()

    def create_widgets(self):
        # Frame for the song list and search
        left_frame = tk.Frame(self.window, padx=10, pady=10)
        left_frame.pack(side="left", fill="y")

        # Search functionality
        search_frame = tk.Frame(left_frame)
        search_frame.pack(fill="x", pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 12)).pack(side="left")
        self.search_entry = tk.Entry(search_frame, font=("Arial", 12), width=30)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.search_songs)

        # Song Listbox
        self.song_list = tk.Listbox(left_frame, font=("Arial", 12), width=40, height=30)
        self.song_list.pack(side="left", fill="y", expand=True)
        self.song_list.bind("<<ListboxSelect>>", self.on_song_select)

        # Scrollbar for the listbox
        scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=self.song_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.song_list.config(yscrollcommand=scrollbar.set)

        # Frame for displaying song content
        right_frame = tk.Frame(self.window, padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True)

        self.song_title = tk.Label(right_frame, text="Select a Song", font=("Arial", 18, "bold"), wraplength=500)
        self.song_title.pack(pady=10)

        self.song_content = scrolledtext.ScrolledText(right_frame, font=("Arial", 14), wrap="word", state="disabled")
        self.song_content.pack(fill="both", expand=True)

    def on_song_select(self, event):
        """Displays the content of the selected song."""
        selected_indices = self.song_list.curselection()
        if not selected_indices:
            return

        selected_song_item = self.song_list.get(selected_indices[0])
        song_id = selected_song_item.split(" - ")[0]

        try:
            conn = get_db_connection()
            if not conn:
                return

            cursor = conn.cursor()
            cursor.execute("SELECT title, content FROM son WHERE id=?", (song_id,))
            song = cursor.fetchone()
            conn.close()

            if song:
                self.song_title.config(text=song[0])
                self.song_content.config(state="normal")
                self.song_content.delete("1.0", tk.END)
                self.song_content.insert(tk.END, song[1])
                self.song_content.config(state="disabled")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch song content: {e}")

    def load_songs(self, search_term=""):
        """Loads songs from the database, optionally filtered by a search term."""
        self.song_list.delete(0, tk.END)
        try:
            conn = get_db_connection()
            if not conn:
                return

            cursor = conn.cursor()
            if search_term:
                cursor.execute("SELECT id, title FROM son WHERE title LIKE ? ORDER BY title", (f"%{search_term}%",))
            else:
                cursor.execute("SELECT id, title FROM son ORDER BY title")

            songs = cursor.fetchall()
            conn.close()

            for song in songs:
                self.song_list.insert(tk.END, f"{song[0]} - {song[1]}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load songs: {e}")

    def search_songs(self, event):
        """Filters the song list based on the search term."""
        search_term = self.search_entry.get().strip()
        self.load_songs(search_term)

# --- Main Execution ---
if __name__ == "__main__":
    # Check for the database before starting the app
    if not os.path.exists(DB_PATH):
        messagebox.showerror("Database Error", "The song database was not found. Please run the admin interface to create it.")
        exit()

    root = tk.Tk()
    app = UserApp(root)
    root.mainloop()
