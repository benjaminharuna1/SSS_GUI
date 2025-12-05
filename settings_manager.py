import json
import os

SETTINGS_FILE = 'settings.json'

DEFAULT_SETTINGS = {
    'lines_per_group': 2,
    'split_verses_chorus': True
}

def load_settings():
    """Loads settings from the settings file."""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            return {**DEFAULT_SETTINGS, **settings}
    except (IOError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Saves settings to the settings file."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except IOError:
        return False

def is_section_header(line):
    """Check if a line is a section header (Verse, Chorus, etc.)"""
    line = line.strip()
    if not line:
        return False
    # Check for bracketed headers like [Verse]
    if line.startswith('[') and line.endswith(']'):
        return True
    # Check for text headers like "Verse 1.", "Chorus", "Bridge", etc.
    section_keywords = ['verse', 'chorus', 'bridge', 'pre-chorus', 'outro', 'intro', 'refrain', 'coda']
    lower_line = line.lower()
    for keyword in section_keywords:
        if lower_line.startswith(keyword):
            return True
    return False

def format_lyrics(lyrics, lines_per_group, split_verses_chorus):
    """Formats lyrics based on settings."""
    if not split_verses_chorus:
        return lyrics
    
    lines = lyrics.split('\n')
    formatted_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Handle section headers
        if is_section_header(line):
            formatted_lines.append(line)
            i += 1
        elif not line:
            # Skip empty lines
            i += 1
        else:
            # Collect all lyric lines until next section or end
            group = []
            while i < len(lines):
                current_line = lines[i].strip()
                if not current_line:
                    i += 1
                    break
                if is_section_header(current_line):
                    break
                group.append(current_line)
                i += 1
            
            # Split group into chunks of lines_per_group
            if group:
                for j in range(0, len(group), lines_per_group):
                    chunk = group[j:j + lines_per_group]
                    formatted_lines.append('\n'.join(chunk))
    
    return '\n'.join(formatted_lines)
