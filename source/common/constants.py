"""Application constants"""

from os import path, getenv

def get_config_path():
    """Get configuration file path following XDG Base Directory spec"""
    xdg_config = getenv('XDG_CONFIG_HOME', path.expanduser('~/.config'))
    return path.join(xdg_config, 'linux-wallpaper-engine', 'config.json')


CONFIG_PATH = get_config_path()
STANDARD_COLS = 6 # not to be used in the code, this is just a fallback.

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

# If your boss asks you how long would it take to change the color scheme, tell him a month and enjoy your vacations :)
UI_COLORS = {
    "bg_primary": "#1F0120",
    "bg_secondary": "#0a0e27",
    "bg_tertiary": "#0f1729",
    "fg_text": "#FFFFFF",
    "fg_text_dark": "#000000",
    "accent_blue": "#004466",
    "accent_blue_light": "#0066aa",
    "accent_cyan": "#00d4ff",
    "accent_cyan_bright": "#00ffff",
    "accent_green": "#00AA44",
    "accent_green_light": "#00CC55",
    "accent_green_success": "#00ff00",
    "accent_orange": "#FFAA00",
    "accent_orange_bright": "#FFA500",
    "accent_purple": "#440044",
    "accent_purple_dark": "#5F1166",
    "accent_red": "#ff3333",
    "accent_yellow": "#ffff00",
    "danger_dark": "#661111",
    "danger_light": "#881111",
    "text_input_bg": "#1a2f4d",
    "text_input_fg": "#FFFFFF",
    "text_input_cursor": "#004466",
    "button_disabled": "#003344",
    "button_cancel": "#444444",
    "bg_canvas": "#222222",
}

THUMB_SIZE = (120, 100)
THUMB_DESIRED_COLUMNS = 8
THUMB_MIN_WIDTH = 80
THUMB_ASPECT_RATIO = 1.12

MAIN_SCRIPT_NAME = "main.sh"

DEFAULT_WALLPAPER_PATH_SUGGESTION = "~/.steam/steam/steamapps/workshop/content/431960"
# For Flatpak reimplementation (NOT SUGGESTED), you must make sure to handle edge cases (steam as .flatpak, .snap, native...)
# A helper script would be needed. Refer to the documentation on commits 60-83.

STEAM_WALLPAPER_ENGINE_APP_ID = "431960"

DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
