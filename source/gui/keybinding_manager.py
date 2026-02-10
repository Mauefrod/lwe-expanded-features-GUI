"""
GUI-level keybinding manager for integration with the application.

NOTE: This module uses traditional Linux keyboard handling.
The systemwide keyboard listener (pynput) has been removed. (Not for anything in particular,
just to reduce complexity and having to debug a different module)

This module remains only gui-level, if you need something accesible from the services or core layer,
you can try to  work with the API coded by agent, or code it yourself, it's out of my scope.

As you can see, this module is TOTTALLY DETATCHED from the actual engine control (main.sh) when it comes
to the logic implementation (as it uses python standard libraries and functions instead of bash scripting),
this module wasn't coded by me but from my project mate who does not know bash scripting, so I'll just keep
the logic as is until I actually have time to refactor it.

Be as it may, you can ALSO use this as an example on how to dettach yourself from my bash engine control and 
implement your own in python, that being side, I don't plan on providing support neither for this module nor
custom implmementations because this will be refactored in the long run anyways.

For keyboard shortcut management, you can either:
1. Use the KeybindingController (this module) - existing approach
2. Use KeyboardShortcutAPI (services.keybinding_api) - recommended new clean API

The KeyboardShortcutAPI provides a cleaner, more explicit interface.
"""

from tkinter import Tk, messagebox
from models.keybindings import KeybindingAction
from services.keybinding_service import KeybindingService
from models.config import ConfigManager
from typing import Callable, Dict # OMG my mate used types, what a time to be alive


class KeybindingController:
    """
    Manages keybinding integration in the GUI.
    Handles key press events and executes corresponding actions.
    """

    def __init__(
        self,
        main_window: Tk,
        config: Dict,
        engine_controller,
        event_handlers,
        gallery_view,
        log_callback: Callable = None
    ):
        """
        Initialize the keybinding controller.
        
        Args:
            main_window: The root Tk window
            config: Configuration dictionary
            engine_controller: Instance of EngineController
            event_handlers: Instance of EventHandlers
            gallery_view: Instance of GalleryView
            log_callback: Optional logging callback
        """
        self.main_window = main_window
        self.config = config
        self.engine_controller = engine_controller
        self.event_handlers = event_handlers
        self.gallery_view = gallery_view
        self.log = log_callback or (lambda msg: None)


        self.keybinding_service = KeybindingService(config, log_callback)


        self._register_action_handlers()


        self._setup_key_bindings()

        self.log("[KEYBIND] KeybindingController initialized")

    def _register_action_handlers(self) -> None:
        """Register handlers for all keybinding actions"""


        self.keybinding_service.register_action_handler(
            KeybindingAction.RUN_CURRENT_CONFIG,
            self._action_run_current_config
        )

        self.keybinding_service.register_action_handler(
            KeybindingAction.STOP_ENGINE,
            self._action_stop_engine
        )


        self.keybinding_service.register_action_handler(
            KeybindingAction.SET_WALLPAPER,
            self._action_set_wallpaper
        )

        self.keybinding_service.register_action_handler(
            KeybindingAction.SELECT_RANDOM,
            self._action_select_random
        )


        self.keybinding_service.register_action_handler(
            KeybindingAction.TOGGLE_RANDOM_MODE,
            self._action_toggle_random_mode
        )

        self.keybinding_service.register_action_handler(
            KeybindingAction.TOGGLE_DELAY_MODE,
            self._action_toggle_delay_mode
        )

        self.keybinding_service.register_action_handler(
            KeybindingAction.TOGGLE_WINDOW_MODE,
            self._action_toggle_window_mode
        )

        self.keybinding_service.register_action_handler(
            KeybindingAction.TOGGLE_ABOVE,
            self._action_toggle_above
        )


        self.keybinding_service.register_action_handler(
            KeybindingAction.NEXT_WALLPAPER,
            self._action_next_wallpaper
        )

        self.keybinding_service.register_action_handler(
            KeybindingAction.PREVIOUS_WALLPAPER,
            self._action_previous_wallpaper
        )

        self.log("[KEYBIND] All action handlers registered")

    def _setup_key_bindings(self) -> None:
        """Setup Tkinter key bindings on the main window"""

        self.main_window.bind("<KeyPress>", self._on_key_press)

    def _on_key_press(self, event) -> None:
        """
        Handle Tkinter key press events.
        
        Args:
            event: Tkinter event object
        """

        key = event.keysym


        modifiers = []
        if event.state & 0x0004:
            modifiers.append('ctrl')
        if event.state & 0x0008:
            modifiers.append('alt')
        if event.state & 0x0001:
            modifiers.append('shift')
        if event.state & 0x0040:
            modifiers.append('super')


        self.keybinding_service.on_key_press(key, modifiers)



    def _action_run_current_config(self) -> None:
        """Run the current configuration"""
        self.log("[KEYBIND] Executing: Run current config")


        if not self.config.get("--dir"):
            self.log("[KEYBIND ACTION] No directory selected")
            messagebox.showwarning(
                "No Directory",
                "Please select a wallpaper directory first"
            )
            return

        self.log("[KEYBIND ACTION] Starting engine with current config")
        self.engine_controller.run_engine()

    def _action_stop_engine(self) -> None:
        """Stop the engine"""
        self.log("[KEYBIND] Executing: Stop engine")
        self.engine_controller.stop_engine()
        self.log("[KEYBIND ACTION] Engine stopped")

    def _action_set_wallpaper(self) -> None:
        """Set a specific wallpaper by opening file picker"""
        self.log("[KEYBIND] Executing: Set wallpaper")

        if not self.config.get("--dir"):
            self.log("[KEYBIND ACTION] No directory selected")
            messagebox.showwarning(
                "No Directory",
                "Please select a wallpaper directory first"
            )
            return

        wallpapers = self.gallery_view._load_wallpapers_from_directory(
            self.config.get("--dir")
        )

        if not wallpapers:
            messagebox.showinfo("No Wallpapers", "No wallpapers found in directory")
            return



        if wallpapers:
            selected = wallpapers[0]
            self.log(f"[KEYBIND ACTION] Setting wallpaper: {selected.id}")
            self.engine_controller.apply_wallpaper(
                selected.id,
                wallpapers,
                "all"
            )

    def _action_select_random(self) -> None:
        """Select a random wallpaper from the current set"""
        self.log("[KEYBIND] Executing: Select random wallpaper")

        if not self.config.get("--dir"):
            self.log("[KEYBIND ACTION] No directory selected")
            messagebox.showwarning(
                "No Directory",
                "Please select a wallpaper directory first"
            )
            return


        try:
            wallpapers = self.gallery_view._load_wallpapers_from_directory(
                self.config.get("--dir")
            )

            if not wallpapers:
                messagebox.showinfo("No Wallpapers", "No wallpapers found")
                return

            import random
            selected = random.choice(wallpapers)

            self.log(f"[KEYBIND ACTION] Randomly selected wallpaper: {selected.id}")
            self.engine_controller.apply_wallpaper(
                selected.id,
                wallpapers,
                "all"
            )
        except Exception as e:
            self.log(f"[KEYBIND ACTION ERROR] {str(e)}")
            messagebox.showerror("Error", f"Failed to select random wallpaper: {str(e)}")

    def _action_toggle_random_mode(self) -> None:
        """Toggle random mode on/off"""
        self.log("[KEYBIND] Executing: Toggle random mode")

        current_state = self.config.get("--random", False)
        new_state = not current_state

        self.config["--random"] = new_state

        if new_state:
            self.config["--delay"]["active"] = False
            self.config["--set"]["active"] = False
            self.log("[KEYBIND ACTION] Random mode: ON")
        else:
            self.log("[KEYBIND ACTION] Random mode: OFF")


        try:
            if hasattr(self.event_handlers.ui.get('flags_panel'), 'random_mode'):
                self.event_handlers.ui['flags_panel'].random_mode.set(new_state)
        except:
            pass

        ConfigManager.save(self.config)

    def _action_toggle_delay_mode(self) -> None:
        """Toggle delay mode on/off"""
        self.log("[KEYBIND] Executing: Toggle delay mode")

        current_state = self.config.get("--delay", {}).get("active", False)
        new_state = not current_state

        self.config["--delay"]["active"] = new_state

        if new_state:
            self.config["--random"] = False
            self.config["--set"]["active"] = False
            self.log("[KEYBIND ACTION] Delay mode: ON")
        else:
            self.log("[KEYBIND ACTION] Delay mode: OFF")


        try:
            if hasattr(self.event_handlers.ui.get('flags_panel'), 'delay_mode'):
                self.event_handlers.ui['flags_panel'].delay_mode.set(new_state)
        except:
            pass

        ConfigManager.save(self.config)

    def _action_toggle_window_mode(self) -> None:
        """Toggle window mode on/off"""
        self.log("[KEYBIND] Executing: Toggle window mode")

        current_state = self.config.get("--window", {}).get("active", False)
        new_state = not current_state

        self.config["--window"]["active"] = new_state

        if new_state:
            self.log("[KEYBIND ACTION] Window mode: ON")
        else:
            self.log("[KEYBIND ACTION] Window mode: OFF")


        try:
            if hasattr(self.event_handlers.ui.get('flags_panel'), 'window_mode'):
                self.event_handlers.ui['flags_panel'].window_mode.set(new_state)
        except:
            pass

        ConfigManager.save(self.config)

    def _action_toggle_above(self) -> None:
        """Toggle --above flag"""
        self.log("[KEYBIND] Executing: Toggle --above flag")

        current_state = self.config.get("--above", False)
        new_state = not current_state

        self.config["--above"] = new_state

        if new_state:
            self.log("[KEYBIND ACTION] Always above: ON")
        else:
            self.log("[KEYBIND ACTION] Always above: OFF")


        try:
            if hasattr(self.event_handlers.ui.get('flags_panel'), 'above_flag'):
                self.event_handlers.ui['flags_panel'].above_flag.set(new_state)
        except:
            pass

        ConfigManager.save(self.config)

    def _action_next_wallpaper(self) -> None:
        """Navigate to next wallpaper in gallery"""
        self.log("[KEYBIND] Executing: Next wallpaper")

        try:
            if hasattr(self.gallery_view, 'scroll_to_next'):
                self.gallery_view.scroll_to_next()
                self.log("[KEYBIND ACTION] Scrolled to next wallpaper")
            else:
                self.log("[KEYBIND ACTION] Gallery navigation not available")
        except Exception as e:
            self.log(f"[KEYBIND ACTION ERROR] {str(e)}")

    def _action_previous_wallpaper(self) -> None:
        """Navigate to previous wallpaper in gallery"""
        self.log("[KEYBIND] Executing: Previous wallpaper")

        try:
            if hasattr(self.gallery_view, 'scroll_to_previous'):
                self.gallery_view.scroll_to_previous()
                self.log("[KEYBIND ACTION] Scrolled to previous wallpaper")
            else:
                self.log("[KEYBIND ACTION] Gallery navigation not available")
        except Exception as e:
            self.log(f"[KEYBIND ACTION ERROR] {str(e)}")

    def get_keybindings_info(self) -> Dict[str, str]:
        """Get information about all keybindings"""
        return self.keybinding_service.get_all_keybindings()
