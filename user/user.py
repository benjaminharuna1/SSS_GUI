import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings_manager

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
        self.window.geometry("1000x700")
        self.settings = settings_manager.load_settings()
        self.current_original_lyrics = ""

        self.create_widgets()
        self.load_all_songs()
        self.load_favorite_songs()
        self.load_indexed_songs()

    def create_widgets(self):
        # Main frames
        left_frame = tk.Frame(self.window, padx=10, pady=10)
        left_frame.pack(side="left", fill="y")

        right_frame = tk.Frame(self.window, padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True)

        # Tabbed interface for song lists
        self.notebook = ttk.Notebook(left_frame)
        self.notebook.pack(expand=True, fill="both")

        # --- All Songs Tab ---
        all_songs_frame = ttk.Frame(self.notebook, width=400, height=600)
        self.notebook.add(all_songs_frame, text="All Songs")

        search_frame = tk.Frame(all_songs_frame)
        search_frame.pack(fill="x", pady=5)
        tk.Label(search_frame, text="Search by Title:", font=("Arial", 12)).pack(side="left")
        self.search_entry = tk.Entry(search_frame, font=("Arial", 12), width=30)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_all_songs)

        self.all_songs_list = tk.Listbox(all_songs_frame, font=("Arial", 12))
        self.all_songs_list.pack(fill="both", expand=True)
        self.all_songs_list.bind("<<ListboxSelect>>", self.on_song_select)

        # --- Favorites Tab ---
        favorites_frame = ttk.Frame(self.notebook, width=400, height=600)
        self.notebook.add(favorites_frame, text="Favorites")

        self.favorites_list = tk.Listbox(favorites_frame, font=("Arial", 12))
        self.favorites_list.pack(fill="both", expand=True)
        self.favorites_list.bind("<<ListboxSelect>>", self.on_favorite_select)

        # --- Index Tab ---
        index_frame = ttk.Frame(self.notebook, width=400, height=600)
        self.notebook.add(index_frame, text="Index")

        id_search_frame = tk.Frame(index_frame)
        id_search_frame.pack(fill="x", pady=5)
        tk.Label(id_search_frame, text="Search by ID:", font=("Arial", 12)).pack(side="left")
        self.id_search_entry = tk.Entry(id_search_frame, font=("Arial", 12), width=10)
        self.id_search_entry.pack(side="left")
        tk.Button(id_search_frame, text="Search", command=self.search_by_id).pack(side="left")

        self.index_list = tk.Listbox(index_frame, font=("Arial", 12))
        self.index_list.pack(fill="both", expand=True)
        self.index_list.bind("<<ListboxSelect>>", self.on_index_select)

        # --- Song Content Display ---
        title_frame = tk.Frame(right_frame)
        title_frame.pack(pady=10, fill="x")
        
        self.song_title = tk.Label(title_frame, text="Select a Song", font=("Arial", 18, "bold"), wraplength=300)
        self.song_title.pack(side="left", expand=True)
        
        button_frame = tk.Frame(title_frame)
        button_frame.pack(side="right", padx=5)
        tk.Button(button_frame, text="Copy Lyrics", command=self.copy_to_clipboard, bg="#2196F3", fg="white").pack(side="left", padx=2)
        tk.Button(button_frame, text="⚙ Settings", command=self.open_settings, bg="#607D8B", fg="white").pack(side="left", padx=2)
        
        self.song_content = scrolledtext.ScrolledText(right_frame, font=("Arial", 14), wrap="word", state="disabled")
        self.song_content.pack(fill="both", expand=True)

    def on_song_select(self, event):
        self.display_song_content(self.all_songs_list, "son", "id")

    def on_favorite_select(self, event):
        self.display_song_content(self.favorites_list, "AddSongs", "_id")

    def on_index_select(self, event):
        self.display_song_content(self.index_list, "son", "id")

    def display_song_content(self, listbox, table_name, id_column):
        selected_indices = listbox.curselection()
        if not selected_indices: return

        selected_item = listbox.get(selected_indices[0])
        song_id = selected_item.split(" - ")[0]

        try:
            conn = get_db_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute(f"SELECT title, content FROM {table_name} WHERE {id_column}=?", (song_id,))
            song = cursor.fetchone()
            conn.close()
            if song:
                self.song_title.config(text=song[0])
                # Store original lyrics for copying
                self.current_original_lyrics = song[1]
                self.song_content.config(state="normal")
                self.song_content.delete("1.0", tk.END)
                # Display formatted lyrics in UI
                formatted = settings_manager.format_lyrics(
                    song[1],
                    self.settings['lines_per_group'],
                    self.settings['split_verses_chorus']
                )
                self.song_content.insert(tk.END, formatted)
                self.song_content.config(state="disabled")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch song content: {e}")

    def load_all_songs(self, search_term=""):
        self.all_songs_list.delete(0, tk.END)
        try:
            conn = get_db_connection()
            if not conn: return
            cursor = conn.cursor()
            if search_term:
                cursor.execute("SELECT id, title FROM son WHERE title LIKE ? ORDER BY title COLLATE NOCASE", (f"%{search_term}%",))
            else:
                cursor.execute("SELECT id, title FROM son ORDER BY title COLLATE NOCASE")
            for song in cursor.fetchall():
                self.all_songs_list.insert(tk.END, f"{song[0]} - {song[1]}")
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load songs: {e}")

    def load_favorite_songs(self):
        self.favorites_list.delete(0, tk.END)
        try:
            conn = get_db_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute("SELECT _id, title FROM AddSongs ORDER BY title COLLATE NOCASE")
            for fav in cursor.fetchall():
                self.favorites_list.insert(tk.END, f"{fav[0]} - {fav[1]}")
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load favorites: {e}")

    def load_indexed_songs(self):
        self.index_list.delete(0, tk.END)
        try:
            conn = get_db_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute("SELECT id, title FROM son ORDER BY id")
            for song in cursor.fetchall():
                self.index_list.insert(tk.END, f"{song[0]} - {song[1]}")
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load songs: {e}")

    def filter_all_songs(self, event):
        self.load_all_songs(self.search_entry.get().strip())

    def search_by_id(self):
        song_id = self.id_search_entry.get().strip()
        if not song_id.isdigit():
            messagebox.showwarning("Invalid Input", "Please enter a valid song ID (number).")
            return

        try:
            conn = get_db_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute("SELECT title, content FROM son WHERE id=?", (song_id,))
            song = cursor.fetchone()
            conn.close()
            if song:
                self.song_title.config(text=song[0])
                # Store original lyrics for copying
                self.current_original_lyrics = song[1]
                self.song_content.config(state="normal")
                self.song_content.delete("1.0", tk.END)
                # Display formatted lyrics in UI
                formatted = settings_manager.format_lyrics(
                    song[1],
                    self.settings['lines_per_group'],
                    self.settings['split_verses_chorus']
                )
                self.song_content.insert(tk.END, formatted)
                self.song_content.config(state="disabled")
            else:
                messagebox.showinfo("Not Found", f"No song found with ID: {song_id}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch song: {e}")

    def copy_to_clipboard(self):
        if not self.current_original_lyrics:
            messagebox.showwarning("No Content", "No lyrics to copy.")
            return
        
        # Format the original lyrics fresh
        formatted = settings_manager.format_lyrics(
            self.current_original_lyrics,
            self.settings['lines_per_group'],
            self.settings['split_verses_chorus']
        )
        
        self.window.clipboard_clear()
        self.window.clipboard_append(formatted)
        self.window.update()
        messagebox.showinfo("Success", "Lyrics copied to clipboard!")

    def open_settings(self):
        settings_window = tk.Toplevel(self.window)
        settings_window.title("Settings")
        settings_window.geometry("400x200")
        settings_window.resizable(False, False)

        # Copy Settings Section
        copy_frame = tk.LabelFrame(settings_window, text="Copy Formatting", padx=10, pady=10, font=("Arial", 11, "bold"))
        copy_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.split_var = tk.BooleanVar(value=self.settings['split_verses_chorus'])
        tk.Checkbutton(copy_frame, text="Split verses and chorus into groups", variable=self.split_var, font=("Arial", 10)).pack(anchor="w", pady=5)

        lines_frame = tk.Frame(copy_frame)
        lines_frame.pack(fill="x", pady=5)
        tk.Label(lines_frame, text="Lines per group:", font=("Arial", 10)).pack(side="left")
        self.lines_var = tk.IntVar(value=self.settings['lines_per_group'])
        lines_spinbox = tk.Spinbox(lines_frame, from_=1, to=5, textvariable=self.lines_var, width=5, font=("Arial", 10))
        lines_spinbox.pack(side="left", padx=5)

        def save_settings():
            self.settings['split_verses_chorus'] = self.split_var.get()
            self.settings['lines_per_group'] = self.lines_var.get()
            if settings_manager.save_settings(self.settings):
                messagebox.showinfo("Success", "Settings saved successfully.")
                settings_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to save settings.")

        tk.Button(copy_frame, text="Save Settings", command=save_settings, bg="#4CAF50", fg="white").pack(pady=5)

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        messagebox.showerror("Database Error", "The song database was not found.")
        exit()

    root = tk.Tk()
    app = UserApp(root)
    root.mainloop()
