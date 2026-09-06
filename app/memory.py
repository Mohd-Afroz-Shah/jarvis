"""
Memory Module

Simple persistent memory for J1.
Stores user preferences and saved notes.
"""

import os
import json
from datetime import datetime

try:
    from .config import NOTES_DIR
except ImportError:  # pragma: no cover - fallback for direct script execution
    from config import NOTES_DIR


def save_note(title, content):
    """
    Save a note to the notes directory.
    
    Args:
        title (str): Note title (used as filename)
        content (str): Note content
    
    Returns:
        bool: Success status
    """
    try:
        # Sanitize filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_title:
            safe_title = "note"
        
        filename = f"{safe_title}.txt"
        filepath = os.path.join(NOTES_DIR, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Created: {datetime.now().isoformat()}\n")
            f.write(f"{'='*40}\n\n")
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"Error saving note: {str(e)}")
        return False


def load_note(title):
    """
    Load a note from the notes directory.
    
    Args:
        title (str): Note title
    
    Returns:
        str: Note content or None if not found
    """
    try:
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_title:
            safe_title = "note"
        
        filename = f"{safe_title}.txt"
        filepath = os.path.join(NOTES_DIR, filename)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            return f.read()
        
    except Exception as e:
        print(f"Error loading note: {str(e)}")
        return None


def list_notes():
    """
    List all saved notes.
    
    Returns:
        list: List of note filenames
    """
    try:
        notes = [f for f in os.listdir(NOTES_DIR) if f.endswith('.txt')]
        return notes
    except Exception as e:
        print(f"Error listing notes: {str(e)}")
        return []
