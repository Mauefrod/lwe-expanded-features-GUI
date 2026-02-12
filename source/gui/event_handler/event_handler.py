from tkinter import filedialog, messagebox, Toplevel, Label, Frame, Button, ttk
from subprocess import Popen, DEVNULL
import os
from models.config import ConfigUpdater
from models.groups import GroupManager
from common.constants import MAIN_SCRIPT_NAME, STEAM_WALLPAPER_ENGINE_APP_ID


class EventHandlers:
    """Centralizes all application event handlers for user interactions"""

    def __init__(self, config, ui_components, log_callback, group_manager=None):
        self.config = config
        self.ui = ui_components
        self.log = log_callback
        # Use injected group manager or create one
        self.group_manager = group_manager or GroupManager(config)



    def on_pick_directory(self) -> None:
        """Handle directory selection from file dialog"""
        route = filedialog.askdirectory()
        if route:
            self.log(f"[HANDLER] Directory selected: {route}")
            self.ui['directory_controls'].set_directory(route)
            ConfigUpdater.set_directory(self.config, route)
            if self.ui.get('on_refresh_gallery'):
                self.ui['on_refresh_gallery']()

    def _open_file_manager(self, dir_path: str) -> bool:
        """
        Open directory in file manager using available tools.
        
        Args:
            dir_path: Path to open
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_managers = ["xdg-open", "thunar", "nautilus"]
        
        for manager in file_managers:
            try:
                Popen([manager, dir_path])
                self.log(f"[HANDLER] Opened directory with {manager}")
                return True
            except FileNotFoundError:
                continue
        
        self.log("[ERROR] Could not open file manager - none available")
        return False

    def on_explore_directory(self) -> None:
        """Open directory in file manager explorer"""
        try:
            dir_path = self.config.get('--dir')
            if not dir_path:
                self.log("[HANDLER] No directory selected")
                messagebox.showwarning(
                    title="No path selected",
                    message="Please, select the Wallpaper Engine Steam Workshop directory before proceeding."
                )
                return

            if not os.path.exists(dir_path):
                self.log(f"[HANDLER] Directory does not exist: {dir_path}")
                messagebox.showerror(
                    title="Directory not found",
                    message=f"The selected directory does not exist:\n{dir_path}"
                )
                return

            self.log(f"[HANDLER] Opening directory explorer for: {dir_path}")
            if not self._open_file_manager(dir_path):
                messagebox.showerror(
                    title="File manager not found",
                    message="Could not open file manager. Please open manually:\n" + dir_path
                )
        except Exception as e:
            self.log(f"[ERROR] Error opening directory: {str(e)}")
            messagebox.showerror(
                title="Error",
                message=f"Error opening directory: {str(e)}"
            )



    def on_window_mode_changed(self) -> None:
        """Handle window mode toggle change"""
        flags = self.ui['flags_panel']
        if flags.window_mode.get():
            self.log("[HANDLER] Window mode enabled")
            ConfigUpdater.set_window_mode(self.config, True)
            self.show_resolution_picker()
        else:
            self.log("[HANDLER] Window mode disabled")
            ConfigUpdater.set_window_mode(self.config, False)

    def on_above_flag_changed(self) -> None:
        """Handle always-on-top flag toggle change"""
        flags = self.ui['flags_panel']
        above_value = flags.above_flag.get()
        ConfigUpdater.set_above_flag(self.config, above_value)
        self.log(f"[HANDLER] Above flag changed to: {above_value}")

    def on_random_mode_changed(self) -> None:
        """Handle random mode toggle change"""
        flags = self.ui['flags_panel']

        if flags.random_mode.get():
            self.log("[HANDLER] Random mode enabled")

            if not self.config["--dir"] or not self.config["--dir"].rstrip("/").endswith(STEAM_WALLPAPER_ENGINE_APP_ID):
                self.log("[HANDLER] Invalid directory for random mode")
                messagebox.showwarning(
                    title="Wrong Directory",
                    message=f"In order for the random mode to work properly, make sure to select the {STEAM_WALLPAPER_ENGINE_APP_ID} folder as your root dir!!"
                )


            flags.add_timer_controls(self.on_timer_submit)
        else:
            self.log("[HANDLER] Random mode disabled")
            ConfigUpdater.set_random_mode(self.config, False)
            flags.clear_dynamic_widgets()

    def on_timer_submit(self, timer_value: str) -> None:
        """Handle timer submission for delay mode"""
        if timer_value != "0":
            self.log(f"[HANDLER] Delay mode set to {timer_value} seconds")
            ConfigUpdater.set_delay_mode(self.config, True, timer_value)
        else:
            self.log("[HANDLER] Random mode (no delay)")
            ConfigUpdater.set_random_mode(self.config, True)

        self.ui['flags_panel'].clear_dynamic_widgets()



    def _handle_sound_setting_change(self, config_key: str, ui_attr: str, log_msg: str) -> None:
        """
        Generic handler for sound panel checkbox changes.
        
        Args:
            config_key: Key within --sound config (e.g., 'silent')
            ui_attr: Attribute name on sound_panel (e.g., 'silent')
            log_msg: Description for logging
        """
        sound_panel = self.ui['sound_panel']
        value = getattr(sound_panel, ui_attr).get()
        ConfigUpdater.set_sound_flag(self.config, config_key, value)
        self.log(f"[HANDLER] {log_msg}: {value}")

        if self.ui.get('on_execute'):
            self.ui['on_execute']()

    def on_silent_changed(self) -> None:
        """Handle silent mode checkbox change"""
        self._handle_sound_setting_change("silent", "silent", "Silent mode")

    def on_noautomute_changed(self) -> None:
        """Handle no auto mute checkbox change"""
        self._handle_sound_setting_change("noautomute", "noautomute", "No auto mute")

    def on_audio_processing_changed(self) -> None:
        """Handle No Audio Processing checkbox change"""
        self._handle_sound_setting_change("no_audio_processing", "no_audio_processing", "No audio processing")




    def show_resolution_picker(self) -> None:
        """Display resolution selection dialog"""
        if hasattr(self, '_resolution_window') and self._resolution_window.winfo_exists():
            return

        from gui.config import RESOLUTIONS

        window = Toplevel(self.ui['main_window'], padx=5)
        window.title("Pick a resolution")
        window.geometry("185x80")
        self._resolution_window = window

        Label(window, text="Pick a resolution").grid(column=0, row=0)
        frame = Frame(window)
        frame.grid(column=0, row=1)

        combo = ttk.Combobox(frame, values=RESOLUTIONS, state="readonly")
        combo.grid(column=0, row=0)

        def accept():
            selected_res = combo.get()
            window.destroy()
            ConfigUpdater.set_window_resolution(self.config, selected_res)

        Button(frame, text="ACCEPT", command=accept).grid(column=0, row=1)


        current = 0
        for n, res in enumerate(RESOLUTIONS):
            if res == self.config["--window"]["res"]:
                current = n
                break

        combo.current(current)



    def on_mousewheel(self, event) -> None:
        """Handle mouse wheel scrolling in gallery view"""
        canvas = self.ui['gallery_canvas'].canvas


        try:
            canvas_height = canvas.winfo_height()
            content_bbox = canvas.bbox("all")
            if not content_bbox:
                return

            content_height = content_bbox[3] - content_bbox[1]


            if content_height <= canvas_height:
                return


            if event.num == 4:
                canvas.yview_scroll(-3, "units")
            elif event.num == 5:
                canvas.yview_scroll(3, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass




    def _get_systemd_manager(self):
        """
        Import and return systemd_manager module.
        
        Returns:
            module: systemd_manager module or None if import fails
        """
        try:
            import sys
            from pathlib import Path

            CURRENT_DIR = Path(__file__).parent.absolute()
            GUI_DIR = CURRENT_DIR.parent
            SOURCE_DIR = GUI_DIR.parent
            CORE_DIR = SOURCE_DIR / "core"

            if str(CORE_DIR) not in sys.path:
                sys.path.insert(0, str(CORE_DIR))

            import systemd_manager
            return systemd_manager
        except Exception as e:
            self.log(f"[ERROR] Failed to import systemd_manager: {str(e)}")
            return None

    def on_startup_changed(self):
        """Handles the startup checkbox toggle"""
        flags = self.ui["flags_panel"]
        enabled = flags.startup.get()

        self.log(f"[HANDLER] Startup toggle changed to: {enabled}")

        try:
            systemd = self._get_systemd_manager()
            if not systemd:
                messagebox.showerror("Startup Configuration Error", "Could not access systemd manager")
                flags.startup.set(not enabled)
                return

            if enabled:
                success, message = systemd.enable_startup()
            else:
                success, message = systemd.disable_startup()

            if success:
                ConfigUpdater.set_startup(self.config, enabled)
                self.log(f"[HANDLER] {message}")
            else:
                self.log(f"[ERROR] {message}")
                messagebox.showerror("Startup Configuration Error", message)
                flags.startup.set(not enabled)

        except Exception as e:
            self.log(f"[ERROR] Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Failed to configure startup: {str(e)}")
            flags.startup.set(not enabled)

    def sync_startup_state(self):
        """Syncs config with actual systemd state on startup"""
        try:
            systemd = self._get_systemd_manager()
            if not systemd:
                return False

            systemd_enabled = systemd.is_service_enabled()
            config_enabled = self.config.get("__run_at_startup__", False)

            if systemd_enabled != config_enabled:
                self.log(f"[HANDLER] Syncing startup state: systemd={systemd_enabled}, config={config_enabled}")
                ConfigUpdater.set_startup(self.config, systemd_enabled)

                if 'flags_panel' in self.ui and hasattr(self.ui['flags_panel'], 'startup'):
                    self.ui['flags_panel'].startup.set(systemd_enabled)

                return systemd_enabled

            return config_enabled

        except Exception as e:
            self.log(f"[ERROR] Failed to sync startup state: {str(e)}")
            return False



    def on_execute(self) -> None:
        """Execute the wallpaper engine with current settings"""
        if self.ui.get('on_execute'):
            self.ui['on_execute']()

    def on_stop(self) -> None:
        """Stop the currently running wallpaper engine"""
        self.log("[GUI] Stopping engine and loops")


        from gui.path_utils import get_script_path

        try:
            script_path = get_script_path(MAIN_SCRIPT_NAME)
        except FileNotFoundError as e:
            self.log(f"[ERROR] {str(e)}")
            messagebox.showerror("Error", f"Could not find {MAIN_SCRIPT_NAME} script")
            return

        try:
            if not os.path.exists(script_path):
                self.log(f"[ERROR] Script not found at: {script_path}")
                messagebox.showerror("Error", f"Script not found at: {script_path}")
                return

            proc = Popen([script_path, "--stop"], stdout=DEVNULL, stderr=DEVNULL)

            import threading
            def wait_and_log():
                returncode = proc.wait()
                if returncode == 0:
                    self.log("[GUI] Engine stop command completed")
                else:
                    self.log(f"[WARNING] Engine stop returned code {returncode}")
            threading.Thread(target=wait_and_log, daemon=True).start()
        except Exception as e:
            self.log(f"[ERROR] Failed to stop engine: {str(e)}")
            messagebox.showerror("Error", f"Failed to stop engine: {str(e)}")



    def on_configure_keybindings(self):
        """Opens the keybinding configuration dialog"""
        try:
            from gui.keybinding_dialog import KeybindingEditorDialog

            self.log("[HANDLER] Opening keybinding editor")
            dialog = KeybindingEditorDialog(
                self.ui['main_window'],
                self.ui.get('keybinding_controller'),
                self.log
            )
            dialog.show()
        except Exception as e:
            self.log(f"[ERROR] Failed to open keybinding editor: {str(e)}")
            messagebox.showerror("Error", f"Failed to open keybinding editor: {str(e)}")