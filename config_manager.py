import json
import os

CONFIG_FILE = 'config.json'

def save_api_key(api_key):
    """Saves the Gemini API key to the config file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'gemini_api_key': api_key}, f, indent=4)
        return True
    except IOError as e:
        print(f"Error saving API key: {e}")
        return False

def load_api_key():
    """Loads the Gemini API key from the config file."""
    if not os.path.exists(CONFIG_FILE):
        return None

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('gemini_api_key')
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading API key: {e}")
        return None
