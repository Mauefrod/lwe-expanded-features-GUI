"""This is not a wrapper :)"""
"""This module is the actual orchestrator of the engine control, it connects the GUI with the services.engine_controller 
module, and provides a backward compatibility layer for the GUI to interact with the engine control without worrying 
about the underlying implementation."""
"""This module as well, handles the initialization of the whole GUI, creating the main window, loading the configuration, 
creating the UI components, connecting the callbacks, etc."""

from tkinter import Tk
from os import path
from typing import Optional, Callable, Dict, Any, List

from gui.config import load_config, merge_config, DEFAULT_CONFIG, save_config
from gui.wallpaper_loader import WallpaperLoader, THUMB_SIZE
from gui.engine_controller import EngineController
from gui.gallery_view.gallery_view import GalleryView
from gui.groups import delete_not_working_wallpapers, set_log_callback


from gui.ui_components.log_area import LogArea
from gui.ui_components.directory_controls import DirectoryControls
from gui.ui_components.flags import FlagsPanel
from gui.ui_components.sound_panel import SoundPanel
from gui.ui_components.gallery_canvas import GalleryCanvas
from gui.event_handler.event_handler import EventHandlers
from gui.gallery_view.gallery_manager import GalleryManager
from gui.keybinding_manager import KeybindingController


class WallpaperEngineGUI:
    """Main GUI application class that orchestrates all UI components and engine interaction"""

    def __init__(self):

        self.main_window = Tk()
        self.main_window.title("Linux Wallpaper Engine GUI")
        self.main_window.config(bg="#1F0120")

        self.main_window.update_idletasks()
        sw = self.main_window.winfo_screenwidth()
        sh = self.main_window.winfo_screenheight()

        geom_w = sw
        geom_h = sh
        self.main_window.geometry(f"{geom_w}x{geom_h}+0+0")
        self.main_window.minsize(800, 600)
        self.main_window.resizable(True, True)

        self.main_window.rowconfigure(1, weight=1)

        self.main_window.rowconfigure(3, weight=0)

        self.main_window.columnconfigure(0, weight=1)
        self.main_window.columnconfigure(1, weight=0)


        self._load_config()


        self.log_area = LogArea(self.main_window)
        self.log_area.grid(column=0, row=3, columnspan=2, sticky="nsew")


        self.loader = WallpaperLoader()
        self.engine = EngineController(DEFAULT_CONFIG, self._log)


        set_log_callback(self._log)


        self._create_ui()


        self._create_gallery_view()


        self._create_managers()


        self._connect_callbacks()


        self._initialize_ui_values()


        self._load_backend_logs()


        self.gallery_manager.refresh()


        self.main_window.protocol("WM_DELETE_WINDOW", self._on_window_close)



    def _load_config(self) -> None:
        """Load and merge configuration from saved state"""
        config = load_config()
        merge_config(DEFAULT_CONFIG, config)
        if DEFAULT_CONFIG["--dir"]:
            expanded_dir = path.expanduser(DEFAULT_CONFIG["--dir"])

            if path.exists(expanded_dir) and path.isdir(expanded_dir):
                DEFAULT_CONFIG["--dir"] = expanded_dir
            else:
                DEFAULT_CONFIG["--dir"] = ""



    def _create_ui(self) -> None:
        """Create all UI components except log_area which is created first"""




        self.directory_controls = DirectoryControls(self.main_window)
        self.directory_controls.grid(column=0, row=0, sticky="nsew")


        self.flags_panel = FlagsPanel(self.main_window)
        self.flags_panel.grid(column=1, row=0, sticky="nsew")


        self.sound_panel = SoundPanel(self.main_window)
        self.sound_panel.grid(column=1, row=1, sticky="nsew", padx=(5, 0), pady=(5, 0))


        self.gallery_canvas = GalleryCanvas(self.main_window)
        self.gallery_canvas.grid(column=0, row=1, columnspan=1, sticky="nsew")

    def _create_gallery_view(self) -> None:
        """Initialize the gallery view for displaying wallpapers and groups"""
        self.gallery_view = GalleryView(
            self.gallery_canvas.canvas,
            self.gallery_canvas.inner_frame,
            DEFAULT_CONFIG,
            self.loader,
            self._log
        )

    def _create_managers(self) -> None:
        """Create and configure application managers (gallery, event handlers, keybindings)"""

        ui_components = {
            'main_window': self.main_window,
            'directory_controls': self.directory_controls,
            'flags_panel': self.flags_panel,
            'sound_panel': self.sound_panel,
            'gallery_canvas': self.gallery_canvas,
            'on_refresh_gallery': lambda: self._refresh_with_scroll_update(),
            'on_execute': self._on_execute
        }


        self.event_handlers = EventHandlers(
            DEFAULT_CONFIG,
            ui_components,
            self._log
        )


        self.gallery_manager = GalleryManager(
            self.gallery_view,
            self.loader,
            DEFAULT_CONFIG
        )

        self.gallery_view.max_cols = getattr(self.gallery_view, "max_cols", 6)



        self.keybinding_controller = KeybindingController(
            self.main_window,
            DEFAULT_CONFIG,
            self.engine,
            self.event_handlers,
            self.gallery_view,
            self._log
        )


        ui_components['keybinding_controller'] = self.keybinding_controller

    def _connect_callbacks(self) -> None:
        """Connect all UI component event callbacks to their respective handlers"""

        self.directory_controls.pick_button.config(
            command=self.event_handlers.on_pick_directory
        )
        self.directory_controls.explore_button.config(
            command=self.event_handlers.on_explore_directory
        )
        self.directory_controls.execute_button.config(
            command=self.event_handlers.on_execute
        )
        self.directory_controls.stop_button.config(
            command=self.event_handlers.on_stop
        )


        self.flags_panel.window_checkbox.config(
            command=self.event_handlers.on_window_mode_changed
        )
        self.flags_panel.above_checkbox.config(
            command=self.event_handlers.on_above_flag_changed
        )
        self.flags_panel.random_checkbox.config(
            command=self.event_handlers.on_random_mode_changed
        )
        self.flags_panel.logs_checkbox.config(
            command=self._on_logs_visibility_changed
        )
        self.flags_panel.back_button.config(
            command=self._on_back
        )
        self.flags_panel.clear_log_button.config(
            command=self.log_area.clear
        )

        self.flags_panel.keybindings_button.config(
            command=self.event_handlers.on_configure_keybindings
        )


        self.sound_panel.silent_checkbox.config(
            command=self.event_handlers.on_silent_changed
        )
        self.sound_panel.noautomute_checkbox.config(
            command=self.event_handlers.on_noautomute_changed
        )
        self.sound_panel.no_audio_processing_checkbox.config(
            command=self.event_handlers.on_audio_processing_changed
        )


        self.gallery_canvas.inner_frame.bind(
            "<Configure>",
            self.gallery_canvas.update_scroll_region
        )
        self.gallery_canvas.bind_scroll_events(
            self.event_handlers.on_mousewheel
        )

        try:
            self.gallery_canvas.canvas.bind("<Configure>", self._on_canvas_resize)
        except Exception:
            pass
        try:
            self.gallery_canvas.container.bind("<Configure>", self._on_canvas_resize)
        except Exception:
            pass
        try:
            self.main_window.bind("<Configure>", self._on_canvas_resize)
        except Exception:
            pass


        self.gallery_view.on_wallpaper_applied = self._on_wallpaper_applied #type:ignore #python is a pain in the as* sometimes
        self.gallery_view.on_refresh_needed = self._refresh_with_scroll_update #type:ignore # same :D, just use Any


        self.flags_panel.startup_checkbox.config(
        command=self.event_handlers.on_startup_changed
        )

    def _initialize_ui_values(self) -> None:
        """Initialize UI component values from saved configuration"""
        self.directory_controls.set_directory(str(DEFAULT_CONFIG["--dir"]))
        self.flags_panel.window_mode.set(DEFAULT_CONFIG["--window"]["active"])

        self.flags_panel.above_flag.set(DEFAULT_CONFIG["--above"])
        self.flags_panel.random_mode.set(
            DEFAULT_CONFIG["--random"] or DEFAULT_CONFIG["--delay"]["active"]
        )
        self.flags_panel.startup.set(DEFAULT_CONFIG.get("__run_at_startup__", False))
        self.event_handlers.sync_startup_state()


        logs_visible = DEFAULT_CONFIG.get("--show-logs", True)
        self.flags_panel.logs_visible.set(logs_visible)

        if logs_visible:
            self.log_area.grid_show()
        else:
            self.log_area.grid_remove()


        sound_config = DEFAULT_CONFIG.get("--sound", {})
        self.sound_panel.silent.set(sound_config.get("silent", False))
        self.sound_panel.noautomute.set(sound_config.get("noautomute", False))
        self.sound_panel.no_audio_processing.set(sound_config.get("no_audio_processing", False))


        try:
            self.main_window.update_idletasks()

            screen_width = self.main_window.winfo_screenwidth()
            col_width = THUMB_SIZE[0]
            initial_cols = max(1, screen_width // col_width) if col_width > 0 else 6
            self.gallery_view.max_cols = initial_cols
        except Exception:
            pass


        self._log_keybindings()

    def _log_keybindings(self) -> None:
        """Log available keybindings to the user at application startup"""
        keybindings_info = self.keybinding_controller.get_keybindings_info()
        if keybindings_info:
            self._log("[KEYBIND] Available keybindings:")
            for action, keybind in keybindings_info.items():
                self._log(f"  {action.replace('_', ' ').title()}: {keybind}")
        else:
            self._log("[KEYBIND] No keybindings configured. Click 'KEYBINDINGS' button to set them up!")


    def _on_canvas_resize(self, event=None) -> None:
        """Handler that recalculates gallery columns based on screen width and thumbnail size"""
        try:

            screen_width = self.main_window.winfo_screenwidth()
            col_width = THUMB_SIZE[0]
            new_cols = max(1, screen_width // col_width) if col_width > 0 else 6
            if new_cols != getattr(self.gallery_view, "max_cols", None):
                self.gallery_view.max_cols = new_cols
                self.gallery_manager.refresh()
        except Exception:
            pass

    def _load_backend_logs(self) -> None:
        """Load and display backend logs if they exist"""
        log_file = path.expanduser(
            "~/.local/share/linux-wallpaper-engine-features/logs.txt"
        )
        if path.exists(log_file):
            with open(log_file, "r") as f:
                for line in f:
                    self._log("[FILE] " + line.strip())



    def _on_wallpaper_applied(self, wallpaper_id: str) -> None:
        """Callback invoked when a wallpaper is applied from the gallery"""



        above_value = self.flags_panel.above_flag.get()


        DEFAULT_CONFIG["--above"] = above_value


        self.engine.apply_wallpaper(
            wallpaper_id,
            self.gallery_view.item_list,
            self.gallery_view.current_view
        )
        self._refresh_with_scroll_update()

    def _on_back(self) -> None:
        """Return to the groups view from wallpapers view"""
        self.gallery_view.go_back()

    def _on_logs_visibility_changed(self) -> None:
        """Handle changes to log area visibility setting"""
        if self.flags_panel.logs_visible.get():
            self.log_area.grid_show()
            self._log("[GUI] Logs visible")
            DEFAULT_CONFIG["--show-logs"] = True
        else:
            self.log_area.grid_remove()
            self._log("[GUI] Logs hidden")
            DEFAULT_CONFIG["--show-logs"] = False
        save_config(DEFAULT_CONFIG)

    def _on_execute(self) -> None:
        """Execute wallpaper engine with current configuration"""
        self._log("[GUI] Deleting 'not working' wallpapers before execution...")
        delete_not_working_wallpapers(DEFAULT_CONFIG)
        self.engine.run_engine(
            self.gallery_view.item_list,
            self.gallery_view.current_view
        )



    def _log(self, message: str) -> None:
        """Centralized logging function that sends messages to the log area"""
        self.log_area.log(message)

    def _refresh_with_scroll_update(self) -> None:
        """Refresh gallery display and update scroll region"""
        self.gallery_manager.refresh()
        self.gallery_canvas.canvas.update_idletasks()
        self.gallery_canvas.update_scroll_region()

    def _on_window_close(self) -> None:
        """Handle window closing event and cleanup resources"""
        self._log("[GUI] Closing application, deleting 'not working' wallpapers...")
        delete_not_working_wallpapers(DEFAULT_CONFIG)
        self._log("[GUI] Cleanup complete, exiting.")
        self.main_window.destroy()



    def run(self) -> None:
        """Start the application main event loop"""
        self.main_window.mainloop()


"""
You could TECHNICALLY create another wrapper around this engine, for the purpose of... idk? 
Adding more abstraction layers or separating concerns even more, but I don't encourage it, at least
I like to work with a monolith orchestrator, makes the codebase more readable
"""


if __name__ == "__main__":
    app = WallpaperEngineGUI()
    app.run()