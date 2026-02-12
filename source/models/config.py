"""Configuration management and persistence"""
"""This is probably the best representation of how the main.sh script works, as this is the abstracted version
in python used for handling all the flags, normalizing data... etc."""
import json
from os import path, makedirs

from common.constants import CONFIG_PATH, RESOLUTIONS


DEFAULT_CONFIG = {
    "__run_at_startup__": False,
    "--window": {
        "active": False,
        "res": "0x0x0x0"
    },
    "--dir": None,
    "--above": False,
    "--delay": {
        "active": False,
        "timer": "0"
    },
    "--random": False,
    "--set": {
        "active": False,
        "wallpaper": ""
    },
    "--sound": {
        "silent": False,
        "noautomute": False,
        "no_audio_processing": False
    },
    "--favorites": [],
    "--groups": {},
    "--pool": [],
    "--keybindings": {
        "bindings": []
    }
}


class ConfigManager:
    """Handles configuration loading, saving, and merging"""

    @staticmethod
    def load():
        """Load configuration from file"""
        if not path.exists(CONFIG_PATH):
            return DEFAULT_CONFIG.copy()

        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG.copy()

    @staticmethod
    def save(config):
        """Save configuration to file"""
        makedirs(path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)

    @staticmethod
    def merge(defaults, loaded):
        """Recursively merge loaded config into defaults"""
        for key, value in loaded.items():
            if key in defaults:
                if isinstance(defaults[key], dict) and isinstance(value, dict):
                    ConfigManager.merge(defaults[key], value)
                else:
                    defaults[key] = value
            else:
                defaults[key] = value


class ConfigValidator:
    """Validates and normalizes configuration values"""

    @staticmethod
    def validate_directory_config(config):
        """Validate directory path in config"""
        dir_path = config.get("--dir")
        if dir_path:
            from os import path as ospath
            expanded = ospath.expanduser(dir_path)
            if ospath.exists(expanded) and ospath.isdir(expanded):
                config["--dir"] = expanded
                return True
            else:
                config["--dir"] = None
                return False
        return True

    @staticmethod
    def validate_resolution(resolution):
        """Check if resolution format is valid"""
        if resolution not in RESOLUTIONS:
            """I don't really know how you would manage to get False in here... but just in case"""
            """So far the resolution values are set as constants in the codebase following the format:
            0x0xwidthxheight, i don't know what the first two 0s are for, but the actual linux-wallpaperengine handles
            it this way"""
            return False
        return True


class ConfigUpdater:
    """Handles configuration state updates"""

    @staticmethod
    def update_set_flag(config):
        """Update --set flag based on random and delay state"""
        if config["--random"] or config["--delay"]["active"]:
            config["--set"]["active"] = False
            config["--set"]["wallpaper"] = ""
        else:
            config["--set"]["active"] = True
            dir_path = config["--dir"]
            if dir_path:
                config["--set"]["wallpaper"] = path.basename(dir_path)

    @staticmethod
    def set_directory(config, dir_path):
        """Update directory and related flags"""
        config["--dir"] = dir_path
        ConfigUpdater.update_set_flag(config)
        ConfigManager.save(config)

    @staticmethod
    def set_random_mode(config, active):
        """Update random mode"""
        config["--random"] = active
        if active:
            config["--delay"]["active"] = False
            config["--set"]["active"] = False
        ConfigUpdater.update_set_flag(config)
        ConfigManager.save(config)

    @staticmethod
    def set_delay_mode(config, active, timer=None):
        """Update delay mode"""
        config["--delay"]["active"] = active
        if timer is not None:
            config["--delay"]["timer"] = timer
        if active:
            config["--random"] = False
            config["--set"]["active"] = False
        ConfigUpdater.update_set_flag(config)
        ConfigManager.save(config)

    @staticmethod
    def set_window_mode(config, active, resolution=None):
        """Update window mode"""
        config["--window"]["active"] = active
        if resolution:
            config["--window"]["res"] = resolution
        ConfigManager.save(config)

    @staticmethod
    def set_above_flag(config, active):
        """Update above flag"""
        config["--above"] = active
        ConfigManager.save(config)

    @staticmethod
    def set_startup(config, active):
        """Update startup flag"""
        config["__run_at_startup__"] = active
        ConfigManager.save(config)

    @staticmethod
    def toggle_above(config):
        """Toggle above flag value"""
        config["--above"] = not config.get("--above", False)
        ConfigManager.save(config)

    @staticmethod
    def set_window_resolution(config, resolution):
        """Set window resolution specifically"""
        if resolution in RESOLUTIONS:
            config["--window"]["res"] = resolution
            ConfigManager.save(config)

    @staticmethod
    def set_pool(config, pool_list):
        """Update the wallpaper pool"""
        config["--pool"] = pool_list if pool_list else []
        ConfigManager.save(config)

    @staticmethod
    def set_sound_flag(config, flag_name, value):
        """Update a single sound flag"""
        valid_flags = ["silent", "noautomute", "no_audio_processing"]
        if flag_name in valid_flags:
            config["--sound"][flag_name] = value
            ConfigManager.save(config)

    @staticmethod
    def set_sound_flags(config, silent=None, noautomute=None, no_audio_processing=None):
        """Update sound configuration flags"""
        if silent is not None:
            config["--sound"]["silent"] = silent
        if noautomute is not None:
            config["--sound"]["noautomute"] = noautomute
        if no_audio_processing is not None:
            config["--sound"]["no_audio_processing"] = no_audio_processing
        ConfigManager.save(config)

    @staticmethod
    def set_wallpaper(config, wallpaper_id):
        """Set a specific wallpaper in --set mode"""
        config["--set"]["active"] = True
        config["--set"]["wallpaper"] = str(wallpaper_id)
        config["--random"] = False
        config["--delay"]["active"] = False
        ConfigManager.save(config)

    @staticmethod
    def set_keybindings(config, keybindings_dict):
        """Update keybindings configuration"""
        config["--keybindings"] = keybindings_dict
        ConfigManager.save(config)
