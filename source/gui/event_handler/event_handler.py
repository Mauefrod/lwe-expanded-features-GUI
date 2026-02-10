from tkinter import filedialog, messagebox, Toplevel, Label, Frame, Button, ttk
from subprocess import Popen, DEVNULL
from os import path
import os
from gui.config import update_set_flag, save_config


class EventHandlers:
    """Centralizes all application event handlers for user interactions"""

    def __init__(self, config, ui_components, log_callback):
        self.config = config
        self.ui = ui_components
        self.log = log_callback



    def on_pick_directory(self) -> None:
        """Handle directory selection from file dialog"""
        route = filedialog.askdirectory()
        if route:
            self.log(f"[HANDLER] Directory selected: {route}")
            self.ui['directory_controls'].set_directory(route)
            self.config["--dir"] = route
            save_config(self.config)
            if self.ui.get('on_refresh_gallery'):
                self.ui['on_refresh_gallery']()

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
            try:
                Popen(["xdg-open", dir_path])
            except FileNotFoundError:
                self.log("[WARNING] xdg-open not found, trying alternatives")

                try:
                    Popen(["thunar", dir_path])
                except:
                    try:
                        Popen(["nautilus", dir_path])
                    except:
                        self.log("[ERROR] Could not open file manager")
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
            self.config["--window"]["active"] = True
            self.show_resolution_picker()
        else:
            self.log("[HANDLER] Window mode disabled")
            self.config["--window"]["active"] = False

    def on_above_flag_changed(self) -> None:
        """Handle always-on-top flag toggle change"""
        flags = self.ui['flags_panel']
        self.config["--above"] = flags.above_flag.get()
        self.log(f"[HANDLER] Above flag changed to: {self.config['--above']}")

    def on_random_mode_changed(self) -> None:
        """Handle random mode toggle change"""
        flags = self.ui['flags_panel']

        if flags.random_mode.get():
            self.log("[HANDLER] Random mode enabled")

            if not self.config["--dir"] or not self.config["--dir"].rstrip("/").endswith("431960"):
                self.log("[HANDLER] Invalid directory for random mode")
                messagebox.showwarning(
                    title="Wrong Directory",
                    message="In order for the random mode to work properly, make sure to select the 431960 folder as your root dir!!"
                )


            flags.add_timer_controls(self.on_timer_submit)
        else:
            self.log("[HANDLER] Random mode disabled")
            self.config["--random"] = False
            self.config["--delay"]["active"] = False
            self.config["--delay"]["timer"] = "0"
            flags.clear_dynamic_widgets()
            save_config(self.config)

        update_set_flag(self.config)

    def on_timer_submit(self, timer_value: str) -> None:
        """Handle timer submission for delay mode"""
        if timer_value != "0":
            self.log(f"[HANDLER] Delay mode set to {timer_value} seconds")
            self.config["--delay"]["active"] = True
            self.config["--delay"]["timer"] = timer_value
            self.config["--random"] = False
        else:
            self.log("[HANDLER] Random mode (no delay)")
            self.config["--delay"]["active"] = False
            self.config["--delay"]["timer"] = "0"
            self.config["--random"] = True

        update_set_flag(self.config)
        save_config(self.config)
        self.ui['flags_panel'].clear_dynamic_widgets()



    def on_silent_changed(self) -> None:
        """Handle silent mode checkbox change"""
        sound_panel = self.ui['sound_panel']
        self.config["--sound"]["silent"] = sound_panel.silent.get()
        self.log(f"[HANDLER] Silent mode: {self.config['--sound']['silent']}")
        save_config(self.config)


        if self.ui.get('on_execute'):
            self.ui['on_execute']()

    def on_noautomute_changed(self) -> None:
        """Handle no auto mute checkbox change"""
        sound_panel = self.ui['sound_panel']
        self.config["--sound"]["noautomute"] = sound_panel.noautomute.get()
        self.log(f"[HANDLER] No auto mute: {self.config['--sound']['noautomute']}")
        save_config(self.config)


        if self.ui.get('on_execute'):
            self.ui['on_execute']()

    def on_audio_processing_changed(self) -> None:
        """Handle No Audio Processing checkbox change"""
        sound_panel = self.ui['sound_panel']
        self.config["--sound"]["no_audio_processing"] = sound_panel.no_audio_processing.get()
        self.log(f"[HANDLER] No audio processing: {self.config['--sound']['no_audio_processing']}")
        save_config(self.config)


        if self.ui.get('on_execute'):
            self.ui['on_execute']()




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
            self.config["--window"]["res"] = selected_res

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




    def on_startup_changed(self):
        """Handles the startup checkbox toggle"""
        flags = self.ui["flags_panel"]
        enabled = flags.startup.get()

        self.log(f"[HANDLER] Startup toggle changed to: {enabled}")

        try:

            import sys
            from pathlib import Path

            CURRENT_DIR = Path(__file__).parent.absolute()
            GUI_DIR = CURRENT_DIR.parent
            SOURCE_DIR = GUI_DIR.parent
            CORE_DIR = SOURCE_DIR / "core"

            if str(CORE_DIR) not in sys.path:
                sys.path.insert(0, str(CORE_DIR))

            from systemd_manager import enable_startup, disable_startup


            if enabled:
                success, message = enable_startup()
            else:
                success, message = disable_startup()

            if success:
                self.config["__run_at_startup__"] = enabled
                save_config(self.config)
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

            import sys
            from pathlib import Path

            CURRENT_DIR = Path(__file__).parent.absolute()
            GUI_DIR = CURRENT_DIR.parent
            SOURCE_DIR = GUI_DIR.parent
            CORE_DIR = SOURCE_DIR / "core"

            if str(CORE_DIR) not in sys.path:
                sys.path.insert(0, str(CORE_DIR))

            from systemd_manager import is_service_enabled

            systemd_enabled = is_service_enabled()
            config_enabled = self.config.get("__run_at_startup__", False)

            if systemd_enabled != config_enabled:
                self.log(f"[HANDLER] Syncing startup state: systemd={systemd_enabled}, config={config_enabled}")
                self.config["__run_at_startup__"] = systemd_enabled
                save_config(self.config)


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
            script_path = get_script_path("main.sh")
        except FileNotFoundError as e:
            self.log(f"[ERROR] {str(e)}")
            messagebox.showerror("Error", "Could not find main.sh script")
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