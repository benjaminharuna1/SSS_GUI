import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3
import os
import config_manager
import google.generativeai as genai

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
        self.window.geometry("1200x800")

        self.selected_song_id = None
        self.selected_favorite_id = None
        self.api_key = config_manager.load_api_key()
        if self.api_key:
            genai.configure(api_key=self.api_key)

        self.create_widgets()
        self.load_songs()
        self.load_favorites()

    def create_widgets(self):
        # Main frames
        top_frame = tk.Frame(self.window, padx=10, pady=10)
        top_frame.pack(side="top", fill="x")

        main_content_frame = tk.Frame(self.window, padx=10, pady=10)
        main_content_frame.pack(side="top", fill="both", expand=True)

        management_frame = tk.Frame(main_content_frame, padx=10, pady=10)
        management_frame.pack(side="left", fill="both", expand=True)

        favorites_frame = tk.Frame(main_content_frame, padx=10, pady=10, bg="#f0f0f0")
        favorites_frame.pack(side="right", fill="both", expand=True)

        # --- API Key Management ---
        api_frame = tk.Frame(top_frame)
        api_frame.pack(fill="x", pady=5)

        tk.Label(api_frame, text="Gemini API Key:", font=("Arial", 12)).pack(side="left")
        self.api_key_entry = tk.Entry(api_frame, font=("Arial", 12), width=50, show="*")
        self.api_key_entry.pack(side="left", padx=5)
        if self.api_key:
            self.api_key_entry.insert(0, self.api_key)
        tk.Button(api_frame, text="Save Key", command=self.save_api_key).pack(side="left")

        # --- Song Management Widgets ---
        input_frame = tk.Frame(management_frame, padx=10, pady=10)
        input_frame.pack(fill="x", side="top")

        tk.Label(input_frame, text="Title:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.title_entry = tk.Entry(input_frame, font=("Arial", 12), width=50)
        self.title_entry.grid(row=0, column=1, sticky="ew")

        tk.Label(input_frame, text="Content:", font=("Arial", 12)).grid(row=1, column=0, sticky="nw", pady=5)
        self.content_text = scrolledtext.ScrolledText(input_frame, font=("Arial", 12), width=60, height=10)
        self.content_text.grid(row=1, column=1, columnspan=3, pady=5)

        tag_frame = tk.Frame(input_frame)
        tag_frame.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        tk.Button(tag_frame, text="[Chorus]", command=lambda: self.insert_tag("[Chorus]\n")).pack(side="left", padx=5)
        tk.Button(tag_frame, text="[Verse]", command=lambda: self.insert_tag("[Verse]\n")).pack(side="left")
        tk.Button(tag_frame, text="Auto-Correct with Gemini", command=self.autocorrect_lyrics, bg="#4285F4", fg="white").pack(side="left", padx=5)


        button_frame = tk.Frame(management_frame, padx=10, pady=10)
        button_frame.pack(fill="x", side="top")
        tk.Button(button_frame, text="Add Song", command=self.add_song, bg="#4CAF50", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="Update Song", command=self.update_song, bg="#FFC107", fg="black").pack(side="left", padx=5)
        tk.Button(button_frame, text="Delete Song", command=self.delete_song, bg="#F44336", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear Fields", command=self.clear_fields, bg="#607D8B", fg="white").pack(side="left", padx=5)

        list_frame = tk.Frame(management_frame, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True)

        self.song_list = tk.Listbox(list_frame, font=("Arial", 12), height=20)
        self.song_list.pack(side="left", fill="both", expand=True)
        self.song_list.bind("<<ListboxSelect>>", self.on_song_select)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.song_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.song_list.config(yscrollcommand=scrollbar.set)

        # --- Favorites Management Widgets ---
        tk.Label(favorites_frame, text="Favorites", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

        fav_button_frame = tk.Frame(favorites_frame, bg="#f0f0f0")
        fav_button_frame.pack(fill="x", pady=5)
        tk.Button(fav_button_frame, text="Add to Favorites", command=self.add_to_favorites, bg="#2196F3", fg="white").pack(side="left", padx=5)
        tk.Button(fav_button_frame, text="Remove from Favorites", command=self.remove_from_favorites, bg="#F44336", fg="white").pack(side="left", padx=5)

        fav_list_frame = tk.Frame(favorites_frame, padx=10, pady=10, bg="#f0f0f0")
        fav_list_frame.pack(fill="both", expand=True)

        self.favorites_list = tk.Listbox(fav_list_frame, font=("Arial", 12), height=20)
        self.favorites_list.pack(side="left", fill="both", expand=True)
        self.favorites_list.bind("<<ListboxSelect>>", self.on_favorite_select)

        fav_scrollbar = tk.Scrollbar(fav_list_frame, orient="vertical", command=self.favorites_list.yview)
        fav_scrollbar.pack(side="right", fill="y")
        self.favorites_list.config(yscrollcommand=fav_scrollbar.set)

    def save_api_key(self):
        new_key = self.api_key_entry.get().strip()
        if not new_key:
            messagebox.showwarning("Input Error", "API key cannot be empty.")
            return
        if config_manager.save_api_key(new_key):
            self.api_key = new_key
            genai.configure(api_key=self.api_key)
            messagebox.showinfo("Success", "API key saved and configured successfully.")
        else:
            messagebox.showerror("Error", "Failed to save API key.")

    def autocorrect_lyrics(self):
        if not self.api_key:
            messagebox.showwarning("API Key Missing", "Please enter and save your Gemini API key first.")
            return

        original_lyrics = self.content_text.get("1.0", tk.END).strip()
        if not original_lyrics:
            messagebox.showwarning("Input Error", "No lyrics to correct.")
            return

        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"Please correct any spelling or grammatical errors in the following song lyrics. Preserve the original line breaks and stanza structure:\n\n{original_lyrics}"
            response = model.generate_content(prompt)

            corrected_lyrics = response.text
            self.content_text.delete("1.0", tk.END)
            self.content_text.insert(tk.END, corrected_lyrics)
            messagebox.showinfo("Success", "Lyrics auto-corrected with Gemini.")

        except Exception as e:
            messagebox.showerror("Gemini API Error", f"An error occurred: {e}")

    def on_song_select(self, event):
        selected_indices = self.song_list.curselection()
        if not selected_indices: return
        selected_item = self.song_list.get(selected_indices[0])
        self.selected_song_id = selected_item.split(" - ")[0]

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
            messagebox.showerror("Database Error", f"Failed to fetch song: {e}")

    def on_favorite_select(self, event):
        selected_indices = self.favorites_list.curselection()
        if not selected_indices: return
        selected_item = self.favorites_list.get(selected_indices[0])
        self.selected_favorite_id = selected_item.split(" - ")[0]

    def add_song(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        if not title or not content:
            messagebox.showwarning("Input Error", "Title and content are required.")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO son (title, content) VALUES (?, ?)", (title, content))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Song added.")
            self.clear_fields()
            self.load_songs()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add song: {e}")

    def update_song(self):
        if not self.selected_song_id:
            messagebox.showwarning("Selection Error", "Select a song to update.")
            return
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        if not title or not content:
            messagebox.showwarning("Input Error", "Title and content are required.")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE son SET title=?, content=? WHERE id=?", (title, content, self.selected_song_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Song updated.")
            self.clear_fields()
            self.load_songs()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update song: {e}")

    def delete_song(self):
        if not self.selected_song_id:
            messagebox.showwarning("Selection Error", "Select a song to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete this song?"):
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM son WHERE id=?", (self.selected_song_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Song deleted.")
            self.clear_fields()
            self.load_songs()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete song: {e}")

    def add_to_favorites(self):
        if not self.selected_song_id:
            messagebox.showwarning("Selection Error", "Select a song to add to favorites.")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT title, content FROM son WHERE id=?", (self.selected_song_id,))
            song = cursor.fetchone()
            if song:
                cursor.execute("INSERT INTO AddSongs (_id, title, content) VALUES (?, ?, ?)", (self.selected_song_id, song[0], song[1]))
                conn.commit()
                messagebox.showinfo("Success", "Added to favorites.")
                self.load_favorites()
            conn.close()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Duplicate", "This song is already in favorites.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add to favorites: {e}")

    def remove_from_favorites(self):
        if not self.selected_favorite_id:
            messagebox.showwarning("Selection Error", "Select a favorite to remove.")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM AddSongs WHERE _id=?", (self.selected_favorite_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Removed from favorites.")
            self.load_favorites()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to remove favorite: {e}")

    def load_songs(self):
        self.song_list.delete(0, tk.END)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title FROM son ORDER BY title COLLATE NOCASE")
            for song in cursor.fetchall():
                self.song_list.insert(tk.END, f"{song[0]} - {song[1]}")
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load songs: {e}")

    def load_favorites(self):
        self.favorites_list.delete(0, tk.END)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT _id, title FROM AddSongs ORDER BY title COLLATE NOCASE")
            for fav in cursor.fetchall():
                self.favorites_list.insert(tk.END, f"{fav[0]} - {fav[1]}")
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load favorites: {e}")

    def clear_fields(self):
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)
        self.song_list.selection_clear(0, tk.END)
        self.selected_song_id = None

    def insert_tag(self, tag):
        self.content_text.insert(tk.INSERT, tag)

if __name__ == "__main__":
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS son (id INTEGER PRIMARY KEY, title TEXT, content TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS AddSongs (_id INTEGER PRIMARY KEY, title TEXT, content TEXT)")
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to init database: {e}")
        exit()

    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()
