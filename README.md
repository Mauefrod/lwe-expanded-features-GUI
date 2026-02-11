# 🎨 Linux Wallpaper Engine Expanded Features GUI

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)

**A modern, responsive graphical interface for managing dynamic wallpapers on Linux**

[Features](#-features) •
[Installation](#-installation) •
[Usage](#-usage) •
[Architecture](#-architecture) •
[Credits](#-credits) •
[Contributing](#-contributing)

</div>


## 📖 About

<details>

**Linux Wallpaper Engine GUI** is a desktop application that provides an intuitive and feature-rich interface for managing and applying dynamic wallpapers on Linux systems. It leverages the power of [linux-wallpaperengine](https://github.com/Acters/linux-wallpaperengine) to bring the Wallpaper Engine experience to Linux users with additional GUI enhancements, organization tools, and automation features.
</details>

---



## ✨ Features

<details>

### Core Features
- 🖼️ **Visual Gallery** - Browse wallpapers with thumbnail previews
- 📁 **Group Organization** - Create and manage wallpaper groups/collections
- ⭐ **Favorites System** - Quick access to your preferred wallpapers
- 🎲 **Random Mode** - Automatic wallpaper rotation  
- ⏱️ **Delay/Timer Mode** - Set wallpapers to change at specific time intervals
- 🪟 **Window Mode** - Run wallpapers as actual windows with custom resolutions
- 🔼 **Always-on-Top Control** - Toggle window layering behavior
- 🔊 **Advanced Sound Control** - Multiple audio options including silent, noautomute, and no audio processing
- 📊 **Real-time Logging** - Monitor application and engine activity
- 💾 **Persistent Configuration** - Settings saved to `~/.config/linux-wallpaper-engine-features/config.json`
- 🔁 **Collapsible UI Sections** - Show or hide panels to customize the interface
- ⌨️ **Keybinding Support** - Custom keyboard shortcuts for actions
- 🚀 **Startup Integration** - Option to run wallpaper automatically on system boot via systemd

### Architecture Features
- **Backward Compatibility Wrappers** - `gui/` modules provide stable APIs for underlying services
- **Type Annotations** - Full Python type hints for better IDE support and code clarity
- **Modular Services** - Business logic separated from GUI presentation
- **Event-Driven Architecture** - Central event handler for user interactions
- **Configuration Persistence** - JSON-based configuration with defaults
- **Process Management** - Direct control over wallpaper engine lifecycle

</details>

---

## 📋 Requirements

<details>

### System Requirements
- **Operating System**: Linux (Ubuntu, Arch, Fedora, Debian, etc.)
- **Python**: 3.10 or higher
- **Display Server**: X11 (Wayland support through linux-wallpaperengine)

### System Dependencies
- `wmctrl` - Window management tool
- `xdotool` - X11 automation tool
- `python3-tk` - Tkinter GUI framework
- `python3-pil` or `python3-pillow` - Image processing library

### Backend Engine
- **[linux-wallpaperengine](https://github.com/Acters/linux-wallpaperengine)** - The core wallpaper engine
  - Install from: https://github.com/Acters/linux-wallpaperengine/tree/wayland-layer-cli
  - This is required to use wallpapers from Wallpaper Engine

---

</details>

---

## 🚀 Installation

<details>

### Automated Installation (Recommended)

```bash
git clone <repository-url>
cd linux-wallpaper-engine-features
chmod +x install.sh
# Interactive install (recommended)
./install.sh

# Non-interactive install without installing OS packages (e.g., in containers)
./install.sh --non-interactive --skip-system-deps

# Dry run to show actions without making changes
./install.sh --dry-run
```

The installer will:
1. Detect your package manager (apt, pacman, dnf, zypper)
2. Install required system dependencies (wmctrl, xdotool, python3-tk, python3-pillow) unless `--skip-system-deps` is passed
3. Create and/or activate a Python virtual environment (default: `.venv`)
4. Install Python dependencies from `requirements.txt`
5. Set executable permissions on scripts and create application directories

Installer options:
- `--skip-system-deps` — Do not attempt to install OS packages (useful on minimal or locked-down systems)
- `--non-interactive` — Do not prompt for confirmation (assume yes where reasonable)
- `--dry-run` — Show the commands that would be executed without making changes
- `--venv-path <path>` — Create virtual environment at a custom path
- `--install-backend` — Try to clone the `linux-wallpaperengine` backend if it is not found (requires `git`)

Notes:
- `tkinter` is provided by your OS package manager; it is **not** installed via pip. On Debian/Ubuntu the package is `python3-tk`, on Fedora `python3-tkinter` etc.
- If the backend `linux-wallpaperengine` is not installed you can use `--install-backend` or follow the backend's README to install it manually.
- To reproduce the exact virtual environment used by the project maintainer, the repository includes `requirements.lock.txt` with pinned package versions; `install.sh` prefers this lockfile when present and will install those exact versions to create an identical `.venv`.

### Manual Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd linux-wallpaper-engine-features
   ```

2. **Install system dependencies** (choose for your distro):

   **Ubuntu/Debian**:
   ```bash
   sudo apt update
   sudo apt install -y wmctrl xdotool python3-tk python3-pil python3-venv
   ```

   **Arch Linux**:
   ```bash
   sudo pacman -Sy --noconfirm wmctrl xdotool tk python-pillow python-virtualenv
   ```

   **Fedora**:
   ```bash
   sudo dnf install -y wmctrl xdotool python3-tkinter python3-pillow python3-virtualenv
   ```

3. **Create and activate virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up backend**:
   ```bash
   chmod +x source/core/main.sh
   mkdir -p ~/.local/share/linux-wallpaper-engine-features/
   ```

### Install linux-wallpaperengine Backend

The application requires the linux-wallpaperengine backend to function:

```bash
# Clone and install linux-wallpaperengine
git clone https://github.com/Acters/linux-wallpaperengine.git
cd linux-wallpaperengine
# Follow the installation instructions in their README
```

Ensure `linux-wallpaperengine` is installed and in your PATH.

---

</details>

---

## 📖 Usage

<details>

### Running the Application

```bash
./source/run.sh
```

Or manually:
```bash
source .venv/bin/activate
cd source
python3 GUI.py
```

### Basic Workflow

1. **Set Wallpaper Directory**:
   - Click "PICK DIR" to select your Wallpaper Engine directory
   - Usually located at: `~/.steam/steam/steamapps/workshop/content/431960/`
   - Or your custom wallpaper collection directory

2. **Browse Wallpapers**:
   - Thumbnails will load automatically
   - Scroll through the gallery to preview available wallpapers

3. **Apply a Wallpaper**:
   - Click on any thumbnail to apply it immediately
   - The wallpaper will start running

4. **Organize with Groups**:
   - Use the group selection to filter wallpapers by category
   - Create custom groups for easier navigation

5. **Use Random Mode**:
   - Check "random mode" to enable automatic rotation
   - Set the interval (delay) between changes
   - The application will cycle through available wallpapers

6. **Configure Options**:
   - **Window Mode**: Run wallpapers as actual windows
   - **Remove Above Priority**: Remove always-on-top behavior (recommended)
   - **Show Logs**: View real-time application logs
   - **Sound Control**: Configure audio playback behavior for wallpapers
   - **Json Config**: The provided config.json in [source/core/config_example.json] is merely an example. The real
   config.json is stored at [~/.config/linux-wallpaper-engine-features/]
---

</details>

---

## 🏗️ Architecture

<details>

### Project Structure

```
linux-wallpaper-engine-features/
├── source/
│   ├── GUI.py                 # Main application entry point
│   ├── gui/                   # All GUI logic and controllers
│   │   ├── gui_engine.py      # High-level GUI controller
│   │   ├── config.py          # Configuration management and persistence
│   │   ├── wallpaper_loader.py# Thumbnail & preview loading + caching
│   │   ├── engine_controller.py# Starts/stops backend engine and manages flags
│   │   ├── event_handler/     # User event processing
│   │   ├── gallery_view/      # Gallery management and rendering
│   │   └── ui_components/     # Reusable UI widgets (buttons, panels)
│   └── core/
│       └── main.sh            # Helper shell scripts used by the backend
├── install.sh                  # Native installer (recommended)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Runtime overview

- **Process flow**: The user interacts with the UI (`GUI.py` → `gui/`), which delegates wallpaper application tasks to the `Engine Controller` (`engine_controller.py`). The controller launches and communicates with the `linux-wallpaperengine` backend (a CLI/binary) using command-line flags and by monitoring its process and logs.
- **Thumbnail & gallery**: `wallpaper_loader.py` loads `preview.jpg`/`preview.png` assets and caches thumbnails used by the `gallery_view` and `gallery_manager` to render the visual library.
- **Configuration**: `config.py` persists settings to `~/.config/linux-wallpaper-engine-features/config.json`. Installer-created data and logs are stored under `~/.local/share/linux-wallpaper-engine-features/`.
- **Window & process management**: The app uses system tools (`wmctrl`, `xdotool`) to detect and manipulate wallpaper windows when running in Window Mode or when applying `--above`/priority flags.
- **Packaging**: The `flatpak/` directory contains build manifests and an exported `build-dir` for Flatpak packaging. Flatpak builds package a runtime and sandbox the app, changing how the Engine Controller finds and interacts with external processes.

### Key components (details)

- **GUI Engine (`gui_engine.py`)**: Coordinates UI state, user actions, and high-level workflows (apply, stop, random/delay modes).
- **Engine Controller (`engine_controller.py`)**: Responsible for assembling engine command lines (`--dir`, `--window`, `--above`, `--random`, `--delay`), spawning the backend process, watching stdout/stderr for status, and terminating/cleaning up processes.
- **Wallpaper Loader (`wallpaper_loader.py`)**: Handles scanning wallpaper directories, reading preview images, generating thumbnails, and caching for responsive UI.
- **Gallery Manager / View (`gallery_view/`)**: Manages layout, selection, context menus, and commands to apply wallpapers.
- **Event Handler (`event_handler/`)**: Central event dispatcher for UI interactions and background tasks.
- **Config Manager (`config.py`)**: Loads/saves user preferences and exposes a programmatic API for settings.
- **Core scripts (`source/core/main.sh`) & `install.sh`**: Shell helpers used by the backend and the native installer; `install.sh` is the recommended way to install required system dependencies, create a virtualenv, and prepare the native environment.

### Packaging notes

- **Native build (recommended)**: `install.sh` sets up a native environment where the application has full access to system tools and processes. This results in reliable detection of existing wallpaper windows and correct behavior for `--delay`, `--random`, `--above`, and other window-management features.

---

</details>

---

## 🛠️ Development

<details>

### Setting Up Development Environment

```bash
git clone <repository-url>
cd linux-wallpaper-engine-features
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running in Development Mode

```bash
source .venv/bin/activate
cd source
python3 GUI.py
```

### Code Structure & Architecture

The application uses a **layered architecture** with separation of concerns:

```
┌─────────────────────┐
│   GUI Layer         │  (gui_engine.py, ui_components/)
│   (Presentation)    │
└──────────┬──────────┘
           │
┌──────────v──────────┐
│  Handler Layer      │  (event_handler/, gallery_view/)
│  (User Interaction) │
└──────────┬──────────┘
           │
┌──────────v──────────┐
│  Service Layer      │  (services/)
│  (Business Logic)   │
└──────────┬──────────┘
           │
┌──────────v──────────┐
│  Model Layer        │  (models/)
│  (Data Management)  │
└──────────┬──────────┘
           │
┌──────────v──────────┐
│  Backend Engine     │  (linux-wallpaperengine)
│  (Process Control)  │
└─────────────────────┘
```

### Module Organization

- **`gui/`** - GUI presentation layer and wrappers
  - `gui_engine.py` - Main orchestrator that coordinates all GUI components
  - `config.py` - Backward compatibility wrapper for configuration
  - `groups.py` - Backward compatibility wrapper for group management
  - `wallpaper_loader.py` - Backward compatibility wrapper for wallpaper loading
  - `engine_controller.py` - Backward compatibility wrapper for engine control
  - `event_handler/` - Event processing and user interaction handling
  - `gallery_view/` - Gallery display and management
  - `ui_components/` - Reusable UI widgets (buttons, panels, controls)

- **`services/`** - Business logic and service layer
  - `engine_controller.py` - Core engine control (start/stop, process management)
  - `argument_builder.py` - Builds CLI arguments for the backend
  - `wallpaper_service.py` - Wallpaper discovery and preview loading
  - `keybinding_service.py` - Keybinding management

- **`models/`** - Data models and persistence
  - `config.py` - Configuration management with load/save
  - `groups.py` - Group/collection management
  - `keybindings.py` - Keybinding data structures

- **`common/`** - Shared utilities
  - `logger.py` - Centralized logging
  - `constants.py` - Application constants and configurations
  - `validators.py` - Input validation
  - `path_helpers.py` - Path resolution utilities

### Adding New Features

#### 1. Add a Simple Toggle Option

Example: Adding a new sound control option

```python
# 1. Add to models/config.py DEFAULT_CONFIG
"--sound": {
    "silent": False,
    "noautomute": False,
    "no_audio_processing": False,
    "my_new_option": False  # <- Add here
}

# 2. Create UI component in gui/ui_components/
class MyNewPanel:
    """Manages my new feature controls"""
    
    def __init__(self, parent: Tk):
        self.my_var = BooleanVar(value=False)
        self.checkbox = Checkbutton(parent, text="My Option", variable=self.my_var)
    
    def grid(self, **kwargs) -> None:
        """Position the panel"""
        self.checkbox.grid(**kwargs)

# 3. Add to gui/gui_engine.py initialization
self.my_panel = MyNewPanel(self.main_window)
self.my_panel.grid(column=1, row=2, sticky="nsew")

# 4. Create event handler in gui/event_handler/event_handler.py
def on_my_option_changed(self) -> None:
    """Handle my option change"""
    self.config["--my_new_option"] = self.ui['my_panel'].my_var.get()
    save_config(self.config)
    if self.ui.get('on_execute'):
        self.ui['on_execute']()

# 5. Connect callback in gui/gui_engine.py _connect_callbacks()
self.my_panel.checkbox.config(command=self.event_handlers.on_my_option_changed)

# 6. Update argument_builder.py to pass to backend
def _add_my_option_arg(self, args: List[str]) -> List[str]:
    """Add my option argument if enabled"""
    if self.config.get("--my_new_option", False):
        args.append("--my-option")
    return args
```

#### 2. Add a Search/Filter Feature

Create a new module in `gui/ui_components/search_panel.py`:

```python
from tkinter import Entry, Frame, StringVar

class SearchPanel:
    """Manages wallpaper search and filtering"""
    
    def __init__(self, parent, on_search_callback):
        self.search_var = StringVar()
        self.search_var.trace("w", lambda *args: on_search_callback(self.search_var.get()))
        
        self.frame = Frame(parent)
        self.entry = Entry(self.frame, textvariable=self.search_var)
        self.entry.pack()
    
    def grid(self, **kwargs) -> None:
        self.frame.grid(**kwargs)
    
    def get_search_term(self) -> str:
        return self.search_var.get()
```

#### 3. Type Annotations Best Practices

- Always annotate function parameters and return types
- Use `Optional[T]` for nullable values
- Use `List[T]`, `Dict[K,V]` from `typing` module  
- Use `Union[T1, T2]` for multiple types
- Add type comments for complex logic

```python
from typing import Optional, List, Dict, Callable, Any

def process_wallpapers(
    root_dir: str,
    filter_fn: Optional[Callable[[str], bool]] = None,
    on_complete: Optional[Callable[[List[str]], None]] = None
) -> List[str]:
    """
    Process wallpapers with optional filtering.
    
    Args:
        root_dir: Root wallpaper directory path
        filter_fn: Optional filter function
        on_complete: Optional completion callback
    
    Returns:
        List of wallpaper IDs
    """
    pass
```

### Design Patterns Used

1. **Wrapper Pattern** - `gui/` modules wrap `services/` and `models/` modules
2. **Observer Pattern** - Event callbacks connect UI to handlers
3. **Singleton Pattern** - Global `DEFAULT_CONFIG` object
4. **Facade Pattern** - `gui_engine.py` provides unified interface to GUI components

---

</details>

---

<details>
---

## 🚀 Implementing New Features

<details>

### Quick Start Guide

When adding a new feature to the application, follow this workflow:

#### Step 1: Define Data Model
Add configuration structure in `models/config.py`:

```python
DEFAULT_CONFIG = {
    # ... existing config
    "--my-feature": {
        "enabled": False,
        "option1": "",
        "option2": 0
    }
}
```

#### Step 2: Create Service Layer
Implement business logic in `services/my_service.py`:

```python
"""My feature service implementation"""
from typing import Optional, List, Dict, Any

class MyFeatureService:
    """Handles my feature logic"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def process(self, data: str) -> Optional[str]:
        """Process feature logic"""
        if not self.config["--my-feature"]["enabled"]:
            return None
        return data.upper()
```

#### Step 3: Create UI Component
Create widget in `gui/ui_components/my_feature_panel.py`:

```python
"""UI panel for my feature"""
from tkinter import Frame, BooleanVar, StringVar, Checkbutton, Entry, Label
from typing import Callable, Optional

class MyFeaturePanel:
    """Manages my feature controls"""
    
    def __init__(self, parent: Frame):
        self.frame = Frame(parent, bg="#1F0120")
        self.enabled = BooleanVar(value=False)
        
        self._setup_widgets()
    
    def _setup_widgets(self) -> None:
        """Initialize UI widgets"""
        self.checkbox = Checkbutton(
            self.frame,
            text="Enable My Feature",
            variable=self.enabled,
            bg="#1F0120",
            fg="#FFFFFF"
        )
        self.checkbox.pack(padx=5, pady=5)
    
    def grid(self, **kwargs) -> None:
        """Position the panel"""
        self.frame.grid(**kwargs)
    
    def get_state(self) -> bool:
        """Get current feature state"""
        return self.enabled.get()
```

#### Step 4: Create Event Handler
Add handler method in `gui/event_handler/event_handler.py`:

```python
def on_my_feature_changed(self) -> None:
    """Handle my feature state change"""
    feature_panel = self.ui.get('my_feature_panel')
    if feature_panel:
        self.config["--my-feature"]["enabled"] = feature_panel.get_state()
        save_config(self.config)
        self.log("[HANDLER] My feature changed")
        
        if self.ui.get('on_execute'):
            self.ui['on_execute']()
```

#### Step 5: Integrate in Main GUI
Update `gui/gui_engine.py`:

```python
# In _create_ui()
from gui.ui_components.my_feature_panel import MyFeaturePanel

self.my_feature_panel = MyFeaturePanel(self.main_window)
self.my_feature_panel.grid(column=1, row=3, sticky="nsew", padx=5, pady=5)

# In _create_managers() - add to ui_components dict
ui_components['my_feature_panel'] = self.my_feature_panel

# In _connect_callbacks()
if hasattr(self.my_feature_panel, 'checkbox'):
    self.my_feature_panel.checkbox.config(
        command=self.event_handlers.on_my_feature_changed
    )
```

#### Step 6: Update Backend Integration (if needed)
Modify `services/argument_builder.py`:

```python
def _add_my_feature_arg(self, args: List[str]) -> List[str]:
    """Add my feature argument if configured"""
    if self.config.get("--my-feature", {}).get("enabled", False):
        args.append("--my-feature")
        option = self.config["--my-feature"].get("option1")
        if option:
            args.extend(["--my-feature-option", option])
    return args

# Call from build_arguments()
def build_arguments(self) -> List[str]:
    args = []
    # ... existing code ...
    args = self._add_my_feature_arg(args)
    return args
```

### Code Quality Guidelines

#### Type Annotations
Always use type hints:
```python
from typing import Optional, List, Dict, Callable, Any, Union

def my_function(
    param1: str,
    param2: Optional[int] = None,
    callback: Optional[Callable[[str], None]] = None
) -> Dict[str, Any]:
    """Function with type annotations"""
    return {}
```

#### Docstrings
Use descriptive docstrings:
```python
def process_wallpaper(wallpaper_id: str) -> bool:
    """
    Process and apply a wallpaper.
    
    Args:
        wallpaper_id: Unique wallpaper identifier
    
    Returns:
        True if successfully applied, False otherwise
    
    Raises:
        FileNotFoundError: If wallpaper directory not found
    """
    pass
```

#### Comments
Add comments only where logic is non-obvious:
```python
# Calculate optimal thumbnail width based on screen size and column count
available_width = screen_width - (padding_per_thumb * desired_columns)
thumb_width = max(THUMB_MIN_WIDTH, available_width // desired_columns)
```

#### Error Handling
Always handle exceptions appropriately:
```python
try:
    result = self.service.process(data)
except ValueError as e:
    self.log(f"[ERROR] Invalid data: {e}")
    return False
except Exception as e:
    self.log(f"[ERROR] Unexpected error: {e}")
    import traceback
    self.log(f"[ERROR] Traceback:\n{traceback.format_exc()}")
    return False
```

### Testing Your Feature

1. **Manual Testing**:
   ```bash
   cd source
   python3 GUI.py
   ```

2. **Check Logs**:
   ```bash
   tail -f ~/.local/share/linux-wallpaper-engine-features/logs.txt
   ```

3. **Verify Configuration**:
   ```bash
   cat ~/.config/linux-wallpaper-engine-features/config.json | python3 -m json.tool
   ```

### Common Pitfalls

- ❌ **Not translating docstrings to English** - All new code should use English
- ❌ **Missing type annotations** - Add types for all function parameters and returns
- ❌ **Hardcoding values** - Use `models/config.py` for constants
- ❌ **Not updating config model** - Always update `DEFAULT_CONFIG` first
- ❌ **Skipping error handling** - Wrap external operations in try/except
- ❌ **Not logging user actions** - Use `self.log()` for debugging

### Updating Wrappers

When modifying service layer, remember to update the wrapper in `gui/`:

```python
# In gui/config.py or gui/groups.py
def my_new_function(config, param):
    """Backward compatibility wrapper"""
    manager = MyManager(config)
    return manager.do_something(param)
```

</details>
---
<details>

### Application won't start
- Ensure all system dependencies are installed
- Check that the virtual environment is activated
- Verify Python version is 3.10+

### Wallpapers not appearing
- Ensure linux-wallpaperengine is installed and in PATH
- Verify the wallpaper directory is correctly set
- Check that wallpaper folders contain `preview.jpg` or `preview.png`

### Wallpaper won't apply
- Test with `linux-wallpaperengine` directly
- Check logs in `~/.local/share/linux-wallpaper-engine-features/logs.txt`
- Verify your display manager compatibility

### Random/Delay mode not stopping
- The process should stop automatically; check the logs
- If stuck, kill manually: `pkill -f linux-wallpaperengine`

</details>

---

## 📝 Configuration

<details>

Configuration is stored in `~/.config/linux-wallpaper-engine-features/config.json`. You can manually edit this file to adjust settings:

- `--dir` - Wallpaper directory path
- `--window` - Window mode settings
- `--above` - Always-on-top flag
- `--random` - Random mode enabled
- `--delay` - Auto-change delay settings
- `--sound` - Audio control settings with options for silent, volume, noautomute, and no_audio_processing
- `--show-logs` - Log visibility

---


</details>


---

## 🙏 Credits & Attribution

<details>

### Original Project
This project builds upon and extends:
- **[linux-wallpaperengine](https://github.com/Acters/linux-wallpaperengine)** - A CLI tool to apply Wallpaper Engine projects on Linux
   - A fantastic port of the Wallpaper Engine experience to Linux

### Key Technologies
- **Python 3** - Programming language
- **Tkinter** - GUI framework
- **PIL (Pillow)** - Image processing
- **linux-wallpaperengine** - Backend wallpaper engine

### Special Thanks
- The Wallpaper Engine community for creating amazing wallpapers
- The linux-wallpaperengine project for making this possible on Linux
- All contributors and users providing feedback and improvements

---
</details>

## 📄 License

<details>

This project is released under the **MIT License** - see [LICENSE](LICENSE) file for details.

</details>

---

## 🤝 Contributing

<details>

Contributions are welcome! Here's how you can help:

1. **Report Bugs** - Open an issue with details about the problem
2. **Suggest Features** - Share ideas for improvements
3. **Submit Code** - Create a pull request with your changes
4. **Improve Documentation** - Help make the docs clearer

### Development Guidelines
- Follow PEP 8 style guidelines
- Test your changes before submitting
- Provide clear commit messages
- Document any new features

</details>

---


<details>

For issues, questions, or suggestions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the logs at `~/.local/share/linux-wallpaper-engine-features/logs.txt`
3. Open an issue on the repository

</details>

---

## 🔗 Resources

<details>

- [Wallpaper Engine](https://store.steampowered.com/app/431960/Wallpaper_Engine/) - Steam Workshop
- [linux-wallpaperengine](https://github.com/Acters/linux-wallpaperengine) - Backend project
- [Python Tkinter Docs](https://docs.python.org/3/library/tkinter.html) - GUI framework documentation

</details>

---

**Made with ❤️ for the Linux community**
