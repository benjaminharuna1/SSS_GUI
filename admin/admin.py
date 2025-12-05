import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3
import os

# --- Database Setup ---
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')
DB_PATH = os.path.join(DB_DIR, 'songs.db')

def get_db_connection():
    """Establishes and returns a database connection."""
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

# --- Admin Application ---
class AdminApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Admin Interface - Song Database Management")
        self.window.geometry("1000x700")

        self.selected_song_id = None

        self.create_widgets()
        self.load_songs()

    def create_widgets(self):
        # Frame for input fields
        input_frame = tk.Frame(self.window, padx=10, pady=10)
        input_frame.pack(fill="x", side="top")

        # Title
        tk.Label(input_frame, text="Title:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.title_entry = tk.Entry(input_frame, font=("Arial", 12), width=50)
        self.title_entry.grid(row=0, column=1, sticky="ew")

        # Content
        tk.Label(input_frame, text="Content:", font=("Arial", 12)).grid(row=1, column=0, sticky="nw", pady=5)
        self.content_text = scrolledtext.ScrolledText(input_frame, font=("Arial", 12), width=80, height=15)
        self.content_text.grid(row=1, column=1, columnspan=3, pady=5)

        # Frame for tag buttons
        tag_frame = tk.Frame(input_frame)
        tag_frame.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        tk.Button(tag_frame, text="[Chorus]", command=lambda: self.insert_tag("[Chorus]\n")).pack(side="left", padx=5)
        tk.Button(tag_frame, text="[Verse]", command=lambda: self.insert_tag("[Verse]\n")).pack(side="left")

        # Frame for action buttons
        button_frame = tk.Frame(self.window, padx=10, pady=10)
        button_frame.pack(fill="x", side="top")

        tk.Button(button_frame, text="Add Song", command=self.add_song, bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        tk.Button(button_frame, text="Update Song", command=self.update_song, bg="#FFC107", fg="black", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        tk.Button(button_frame, text="Delete Song", command=self.delete_song, bg="#F44336", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear Fields", command=self.clear_fields, bg="#607D8B", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)

        # Frame for the song list
        list_frame = tk.Frame(self.window, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True)

        # Song Listbox
        self.song_list = tk.Listbox(list_frame, font=("Arial", 12), height=20)
        self.song_list.pack(side="left", fill="both", expand=True)
        self.song_list.bind("<<ListboxSelect>>", self.on_song_select)

        # Scrollbar for the listbox
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.song_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.song_list.config(yscrollcommand=scrollbar.set)

    def on_song_select(self, event):
        """Populates fields when a song is selected from the list."""
        selected_indices = self.song_list.curselection()
        if not selected_indices:
            return

        selected_song_item = self.song_list.get(selected_indices[0])
        self.selected_song_id = selected_song_item.split(" - ")[0]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT title, content FROM son WHERE id=?", (self.selected_song_id,))
            song = cursor.fetchone()
            conn.close()

            if song:
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(tk.END, song[0])
                self.content_text.delete("1.0", tk.END)
                self.content_text.insert(tk.END, song[1])

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch song details: {e}")

    def insert_tag(self, tag):
        """Inserts a tag like [Chorus] or [Verse] into the content text widget."""
        self.content_text.insert(tk.INSERT, tag)

    def add_song(self):
        """Adds a new song to the database."""
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()

        if not title or not content:
            messagebox.showwarning("Input Error", "Title and content cannot be empty.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO son (title, content) VALUES (?, ?)", (title, content))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Song added successfully.")
            self.clear_fields()
            self.load_songs()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add song: {e}")

    def update_song(self):
        """Updates the selected song in the database."""
        if not hasattr(self, 'selected_song_id') or not self.selected_song_id:
            messagebox.showwarning("Selection Error", "Please select a song to update.")
            return

        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()

        if not title or not content:
            messagebox.showwarning("Input Error", "Title and content cannot be empty.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE son SET title=?, content=? WHERE id=?", (title, content, self.selected_song_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Song updated successfully.")
            self.clear_fields()
            self.load_songs()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update song: {e}")

    def delete_song(self):
        """Deletes the selected song from the database."""
        if not hasattr(self, 'selected_song_id') or not self.selected_song_id:
            messagebox.showwarning("Selection Error", "Please select a song to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this song?"):
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM son WHERE id=?", (self.selected_song_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Song deleted successfully.")
            self.clear_fields()
            self.load_songs()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete song: {e}")

    def load_songs(self):
        """Loads all songs from the database and populates the listbox."""
        self.song_list.delete(0, tk.END)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title FROM son ORDER BY title")
            songs = cursor.fetchall()
            conn.close()

            for song in songs:
                self.song_list.insert(tk.END, f"{song[0]} - {song[1]}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load songs: {e}")

    def clear_fields(self):
        """Clears all input fields and resets selection."""
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)
        self.song_list.selection_clear(0, tk.END)
        self.selected_song_id = None

# --- Main Execution ---
if __name__ == "__main__":
    # Ensure the database and table exist
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS son (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
        # Exit if the database can't be set up
        exit()

    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()
