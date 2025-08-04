import os
import random
from typing import List, Optional

# Simple logging helpers
def info(message: str) -> None:
    print(f"[INFO] {message}")

def success(message: str) -> None:
    print(f"[SUCCESS] {message}")

def warning(message: str) -> None:
    print(f"[WARNING] {message}")

def error(message: str) -> None:
    print(f"[ERROR] {message}")

def question(message: str) -> None:
    print(f"[QUESTION] {message}")

# Music selection helpers
def fetch_songs(songs_dir: Optional[str] = None) -> List[str]:
    """Return a list of all mp3 files in the songs directory."""
    if songs_dir is None:
        songs_dir = os.path.join(os.path.dirname(__file__), "songs")
    if not os.path.exists(songs_dir):
        return []
    return [
        os.path.join(songs_dir, name)
        for name in os.listdir(songs_dir)
        if name.lower().endswith(".mp3")
    ]

def choose_random_song() -> Optional[str]:
    """Return a random song from the local songs directory, or None if none exist."""
    songs = fetch_songs()
    return random.choice(songs) if songs else None

# Account configuration
def get_accounts(platform: str):
    """
    Dummy accounts fetcher. The original project loads account information from a cache
    file. This stripped‑down version returns an empty list by default.
    """
    return []

# Configuration helpers
def get_script_sentence_length() -> int:
    """Return the desired number of sentences in the generated script."""
    return 5

def get_image_prompt_llm() -> str:
    """Return the model used for image prompt generation."""
    return "gpt-3.5-turbo"

def get_model() -> str:
    """Return the default language model name."""
    return "gpt-3.5-turbo"

def get_threads() -> int:
    """Return the number of threads for video processing."""
    return 4

def get_font() -> str:
    """Return the default font name."""
    return "Arial"

def get_fonts_dir() -> str:
    """Return the directory containing fonts."""
    return os.path.join(os.path.dirname(__file__), "fonts")

def get_imagemagick_path() -> Optional[str]:
    """Return the ImageMagick path or None if not configured."""
    return None

def get_assemblyai_api_key() -> str:
    """Return the AssemblyAI API key from environment variables, or an empty string."""
    return os.environ.get("ASSEMBLYAI_API_KEY", "")

def equalize_subtitles(subtitles_path: str, line_length: int) -> str:
    """
    Placeholder for subtitle equalization. The original function calls an external
    module to balance subtitle line lengths. In this stripped‑down version, it
    simply returns the input path unchanged.
    """
    return subtitles_path

# Model parser
def parse_model(name: str) -> str:
    """
    Convert a friendly model name into the internal representation expected by g4f.
    In this minimal implementation the input name is returned unchanged.
    """
    return name
