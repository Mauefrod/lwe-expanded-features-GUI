"""Application constants"""

from os import path, getenv

# Configuration paths
def get_config_path():
    """Get configuration file path following XDG Base Directory spec"""
    xdg_config = getenv('XDG_CONFIG_HOME', path.expanduser('~/.config'))
    return path.join(xdg_config, 'linux-wallpaper-engine', 'config.json')


CONFIG_PATH = get_config_path()

# Resolutions
RESOLUTIONS = [
    "0x0x0x0",
    "0x0x800x600",
    "0x0x1024x768",
    "0x0x1280x720",
    "0x0x1366x768",
    "0x0x1600x900",
    "0x0x1920x1080",
    "0x0x2560x1080",
    "0x0x3840x1080",
    "0x0x2560x1440",
    "0x0x3840x2160"
]

# UI Colors
UI_COLORS = {
    "bg_primary": "#1F0120",
    "bg_secondary": "#0a0e27",
    "fg_text": "#FFFFFF",
    "accent_blue": "#004466",
    "accent_red": "#ff3333",
    "accent_light_blue": "#0066aa",
    "danger_dark": "#661111",
    "danger_light": "#881111",
    "text_input_bg": "#1a2f4d",
    "text_input_fg": "#FFFFFF",
    "text_input_cursor": "#004466",
}

# Thumbnail settings
THUMB_SIZE = (120, 100)
THUMB_DESIRED_COLUMNS = 8
THUMB_MIN_WIDTH = 80
THUMB_ASPECT_RATIO = 1.12  # Height to width ratio

# Script names
MAIN_SCRIPT_NAME = "main.sh"

# Default suggested wallpaper path
DEFAULT_WALLPAPER_PATH_SUGGESTION = "~/.steam/steam/steamapps/workshop/content/431960"

# Window geometry
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
