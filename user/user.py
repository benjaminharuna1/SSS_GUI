import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
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
        self.window.geometry("1000x700")

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
        self.song_title = tk.Label(right_frame, text="Select a Song", font=("Arial", 18, "bold"), wraplength=500)
        self.song_title.pack(pady=10)
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
                self.song_content.config(state="normal")
                self.song_content.delete("1.0", tk.END)
                self.song_content.insert(tk.END, song[1])
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
                cursor.execute("SELECT id, title FROM son WHERE title LIKE ? ORDER BY title", (f"%{search_term}%",))
            else:
                cursor.execute("SELECT id, title FROM son ORDER BY title")
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
            cursor.execute("SELECT _id, title FROM AddSongs ORDER BY title")
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
                self.song_content.config(state="normal")
                self.song_content.delete("1.0", tk.END)
                self.song_content.insert(tk.END, song[1])
                self.song_content.config(state="disabled")
            else:
                messagebox.showinfo("Not Found", f"No song found with ID: {song_id}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch song: {e}")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        messagebox.showerror("Database Error", "The song database was not found.")
        exit()

    root = tk.Tk()
    app = UserApp(root)
    root.mainloop()
