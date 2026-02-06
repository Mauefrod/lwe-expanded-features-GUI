"""Script argument builder for wallpaper engine"""

from common.validators import validate_directory
from common.constants import DEFAULT_WALLPAPER_PATH_SUGGESTION
from tkinter import messagebox


class ArgumentBuilder:
    """Builds command-line arguments for the wallpaper engine script"""
    
    def __init__(self, config, log_callback=None, show_gui_warning=False):
        self.config = config
        self.log = log_callback
        self.show_gui_warning = show_gui_warning
    
    def build_arguments(self):
        """
        Build the complete argument list for the engine script
        
        Returns:
            list: Arguments in correct order
        """
        args = []
        
        # 1. --dir
        args = self._add_directory_arg(args)
        
        # 2. --window
        args = self._add_window_arg(args)
        
        # 3. --above
        args = self._add_above_arg(args)
        
        # 4. --pool
        args = self._add_pool_arg(args)
        
        # 5. --sound
        args = self._add_sound_arg(args)
        
        # 6. Main command (delay, random, or set)
        args = self._add_main_command(args)
        
        return args
    
    def _add_directory_arg(self, args):
        """Add --dir argument if valid"""
        dir_path = self.config.get("--dir")
        
        if dir_path:
            is_valid, error_msg = validate_directory(dir_path, self.log)
            
            if is_valid:
                args.extend(["--dir", dir_path])
                if self.log:
                    self.log(f"[CONFIG] Directory validated: {dir_path}")
            else:
                # Directory invalid - notify but continue
                if self.log:
                    self.log(f"[WARNING] {error_msg}")
                    self.log("[WARNING] Application will continue. Please select a valid directory.")
                
                if self.show_gui_warning:
                    messagebox.showwarning(
                        "Invalid Directory",
                        f"The configured directory could not be found:\n\n{dir_path}\n\n"
                        f"Error: {error_msg}\n\n"
                        f"Please use 'PICK DIR' to select a valid wallpaper directory.\n\n"
                        f"Suggested path:\n{DEFAULT_WALLPAPER_PATH_SUGGESTION}"
                    )
        else:
            # No directory configured
            if self.log:
                self.log("[INFO] No directory configured yet")
            
            if self.show_gui_warning:
                messagebox.showinfo(
                    "No Directory Selected",
                    "No wallpaper directory has been selected.\n\n"
                    "Please use 'PICK DIR' to select your wallpaper directory.\n\n"
                    f"Suggested path:\n{DEFAULT_WALLPAPER_PATH_SUGGESTION}"
                )
        
        return args
    
    def _add_window_arg(self, args):
        """Add --window argument if active"""
        window_config = self.config.get("--window", {})
        if isinstance(window_config, dict) and window_config.get("active"):
            res = window_config.get("res", "0x0x0x0")
            args.extend(["--window", res])
        return args
    
    def _add_above_arg(self, args):
        """Add --above argument if set"""
        if self.config.get("--above", False):
            args.append("--above")
        return args
    
    def _add_pool_arg(self, args):
        """Add --pool argument if set"""
        pool = self.config.get("--pool", [])
        if pool and isinstance(pool, list) and len(pool) > 0:
            args.append("--pool")
            args.extend(pool)
        return args
    
    def _add_sound_arg(self, args):
        """Add --sound argument with sound flags if configured"""
        sound_config = self.config.get("--sound", {})
        if isinstance(sound_config, dict):
            sound_flags = []
            
            if sound_config.get("silent", False):
                sound_flags.append("--silent")
            
            if sound_config.get("noautomute", False):
                sound_flags.append("--noautomute")
            
            if sound_config.get("no_audio_processing", False):
                sound_flags.append("--no-audio-processing")
            
            if sound_flags:
                args.append("--sound")
                args.extend(sound_flags)
                if self.log:
                    self.log(f"[CONFIG] Sound flags: {' '.join(sound_flags)}")
        
        return args
    
    def _add_main_command(self, args):
        """Add the main command (delay, random, or set)"""
        delay_config = self.config.get("--delay", {})
        if isinstance(delay_config, dict) and delay_config.get("active"):
            timer = delay_config.get("timer", "0")
            args.extend(["--delay", timer])
        elif self.config.get("--random", False):
            args.append("--random")
        else:
            set_config = self.config.get("--set", {})
            if isinstance(set_config, dict):
                wallpaper = set_config.get("wallpaper", "")
                if wallpaper:
                    args.extend(["--set", wallpaper])
        
        return args
