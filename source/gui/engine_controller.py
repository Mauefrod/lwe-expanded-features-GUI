"""
Backward compatibility wrapper for engine control.
Actual implementation now in services.engine_controller
"""
from services.engine_controller import EngineController as ServiceEngineController
from services.argument_builder import ArgumentBuilder
from gui.config import build_args
from models.config import ConfigManager


class EngineController:
    """Backward compatible wrapper for engine control"""
    
    def __init__(self, config, log_callback=None):
        self.config = config
        self.log_callback = log_callback
        self._engine = ServiceEngineController(config)
        
        # Set logger callback if provided
        if log_callback:
            from common.logger import set_logger_callback
            set_logger_callback(log_callback)
    
    def log(self, message):
        """Log a message if callback is available"""
        if self.log_callback:
            self.log_callback(message)
    
    def stop_engine(self):
        """Stop the current engine"""
        self._engine.stop_engine()
    
    def run_engine(self, item_list=None, current_view=None, show_gui_warning=True):
        """
        Run the wallpaper engine
        
        Args:
            item_list: List of items for pool
            current_view: Current view type
            show_gui_warning: Whether to show GUI warnings
        """
        # Update pool
        self.update_pool(item_list, current_view)
        
        # Build arguments
        args = build_args(self.config, self.log_callback, show_gui_warning)
        
        # If no args, directio is invalid/missing
        if not args:
            self.log("[WARNING] Cannot execute engine: No valid directory configured")
            self.log("[INFO] Please select a valid wallpaper directory using 'PICK DIR'")
            return
        
        # Stop previous engine and run new one
        self.stop_engine()
        self._engine.run_engine(args)
    
    def update_pool(self, item_list, current_view):
        """Update the wallpaper pool"""
        self._engine.update_pool(item_list, current_view)
    
    def apply_wallpaper(self, wallpaper_id, item_list=None, current_view=None, show_gui_warning=True):
        """
        Apply a specific wallpaper
        
        Args:
            wallpaper_id: ID of the wallpaper to apply
            item_list: Current items list
            current_view: Current view type
            show_gui_warning: Whether to show GUI warnings
        """
        # Configure for --set mode
        self.config["--set"]["active"] = True
        self.config["--set"]["wallpaper"] = wallpaper_id
        self.config["--random"] = False
        self.config["--delay"]["active"] = False
        
        # Save configuration
        ConfigManager.save(self.config)
        
        self.log(f"[GUI] Applying wallpaper: {wallpaper_id}")
        self.log(f"[GUI] --above flag status: {self.config.get('--above', False)}")  
        
        # Execute
        self.run_engine(item_list, current_view, show_gui_warning)
