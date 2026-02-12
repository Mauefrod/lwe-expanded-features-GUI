"""Engine control service"""

from subprocess import Popen, PIPE
from threading import Thread
import os

from common.path_helpers import get_script_path
from common.logger import get_logger
from common.constants import MAIN_SCRIPT_NAME
from models.config import ConfigManager, ConfigUpdater


class EngineController:
    """Controls the wallpaper engine process"""

    def __init__(self, config):
        self.config = config
        self.logger = get_logger()
        self.script_path = None
        self._initialize_script_path()

    def _initialize_script_path(self):
        """Initialize and validate script path"""
        try:
            self.script_path = get_script_path(MAIN_SCRIPT_NAME)
            self.logger.component("ENGINE", f"Script path resolved to: {self.script_path}", "DEBUG")
        except FileNotFoundError as e:
            error_msg = f"Cannot locate engine script: {str(e)}"
            self.logger.component("ENGINE", error_msg, "ERROR")
            self.script_path = None

    def stop_engine(self):
        """Stop the current wallpaper engine process"""
        self.logger.component("ENGINE", "Stopping previous engine...")

        if not self.script_path:
            self.logger.component("ENGINE", "Script path not available, cannot stop engine", "WARNING")
            return

        try:
            if not os.path.exists(self.script_path):
                self.logger.component("ENGINE", f"Script not found at: {self.script_path}", "ERROR")
                return

            stop_proc = Popen(
                [self.script_path, "--stop"],
                stdout=PIPE,
                stderr=PIPE,
                text=True
            )
            stdout, stderr = stop_proc.communicate()

            if stop_proc.returncode != 0 and stderr:
                self.logger.component("ENGINE", f"Stop engine error: {stderr}", "ERROR")
            else:
                self.logger.component("ENGINE", "Previous engine stopped")
        except Exception as e:
            self.logger.component("ENGINE", f"Failed to stop engine: {str(e)}", "ERROR")

    def run_engine(self, arguments):
        """
        Run the wallpaper engine with given arguments
        
        Args:
            arguments: List of command-line arguments
        
        Returns:
            bool: True if engine started successfully
        """
        if not self.script_path:
            self.logger.component("ENGINE", "Cannot run engine: Script path not available", "ERROR")
            return False

        try:
            ConfigManager.save(self.config)

            cmd = [self.script_path] + arguments

            thread = Thread(target=self._run_process, args=(cmd,), daemon=True)
            thread.start()

            self.logger.component("ENGINE", f"Engine started with args: {' '.join(arguments)}")
            return True

        except Exception as e:
            self.logger.component("ENGINE", f"Error running engine: {str(e)}", "ERROR")
            return False

    def _run_process(self, cmd):
        """Execute the process (runs in background thread)"""
        try:
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE, text=True)
            stdout, stderr = proc.communicate()

            if stdout:
                self.logger.component("ENGINE", f"Output: {stdout}")
            if stderr:
                self.logger.component("ENGINE", f"Error: {stderr}", "WARNING")

        except Exception as e:
            self.logger.component("ENGINE", f"Process error: {str(e)}", "ERROR")

    def update_pool(self, item_list, current_view):
        """
        Update the wallpaper pool based on current view
        
        Args:
            item_list: List of current items
            current_view: Current view type
        """
        if not (self.config["--random"] or self.config["--delay"]["active"]):
            ConfigUpdater.set_pool(self.config, [])
            return

        if current_view != "wallpapers":
            ConfigUpdater.set_pool(self.config, [])
            return

        ConfigUpdater.set_pool(self.config, item_list.copy() if item_list else [])
