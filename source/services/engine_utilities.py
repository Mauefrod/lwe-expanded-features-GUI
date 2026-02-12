"""services/engine_utilities.py - Unified engine management utilities

This module consolidates functionality currently scattered across bash scripts,
providing a Python implementation that follows DRY principles and integrates
with the existing Python GUI framework.
"""

import os
import sys
import json
import time
import logging
import subprocess
import threading
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import signal


class EngineLogger:
    """Centralized logging for engine operations - replaces bash logging"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or self._get_default_log_file()
        self._ensure_log_directory()
        
        # Configure logger
        self.logger = logging.getLogger("Engine")
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
    
    @staticmethod
    def _get_default_log_file() -> str:
        data_dir = Path.home() / ".local/share/linux-wallpaper-engine-features"
        return str(data_dir / "logs.txt")
    
    def _ensure_log_directory(self):
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def success(self, message: str):
        """Custom log level for successful operations"""
        self.logger.info(f"[SUCCESS] {message}")


class WindowManager:
    """Manages window detection, manipulation, and tracking - replaces bash window handling"""
    
    def __init__(self, logger: EngineLogger):
        self.logger = logger
        self.wmctrl_available = self._check_wmctrl()
        self.xdotool_available = self._check_xdotool()
    
    def _check_wmctrl(self) -> bool:
        """Check if wmctrl is available"""
        try:
            subprocess.run(['wmctrl', '--help'], 
                         capture_output=True, timeout=2)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_xdotool(self) -> bool:
        """Check if xdotool is available"""
        try:
            subprocess.run(['xdotool', '--help'], 
                         capture_output=True, timeout=2)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def find_engine_windows(self) -> List[str]:
        """Find all engine windows using available tools - replaces bash find_engine_windows"""
        patterns = [
            "linux-wallpaperengine",
            "wallpaperengine",
            "steam_app_431960"
        ]
        
        windows = []
        
        # Try wmctrl first
        if self.wmctrl_available:
            try:
                result = subprocess.run(['wmctrl', '-lx'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                for line in result.stdout.split('\n'):
                    for pattern in patterns:
                        if pattern.lower() in line.lower():
                            window_id = line.split()[0]
                            if window_id not in windows:
                                windows.append(window_id)
                            break
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                self.logger.warning(f"wmctrl failed: {e}")
        
        # Fallback to xdotool
        if not windows and self.xdotool_available:
            try:
                result = subprocess.run(['xdotool', 'search', '--name', 'wallpaper'],
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                windows = result.stdout.strip().split('\n')
                windows = [w for w in windows if w]
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                self.logger.warning(f"xdotool failed: {e}")
        
        return windows
    
    def find_window_for_pid(self, pid: int, max_attempts: int = 5) -> Optional[str]:
        """Find window ID for specific process - replaces bash find_window_for_pid"""
        for attempt in range(max_attempts):
            # Try wmctrl with PID
            if self.wmctrl_available:
                try:
                    result = subprocess.run(['wmctrl', '-lp'],
                                          capture_output=True, 
                                          text=True, 
                                          timeout=2)
                    for line in result.stdout.split('\n'):
                        parts = line.split()
                        if len(parts) >= 3 and parts[2] == str(pid):
                            self.logger.debug(f"Found window {parts[0]} for PID {pid}")
                            return parts[0]
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    pass
            
            # Try xdotool
            if self.xdotool_available:
                try:
                    result = subprocess.run(['xdotool', 'search', '--pid', str(pid)],
                                          capture_output=True, 
                                          text=True, 
                                          timeout=2)
                    if result.stdout.strip():
                        window_id = result.stdout.strip().split('\n')[0]
                        self.logger.debug(f"Found window {window_id} for PID {pid}")
                        return window_id
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    pass
            
            if attempt < max_attempts - 1:
                time.sleep(0.2)
        
        return None
    
    def apply_background_flags(self, window_id: str) -> bool:
        """Apply background window flags - replaces bash apply_background_flags"""
        if not self.wmctrl_available:
            self.logger.warning("wmctrl not available, cannot apply flags")
            return False
        
        success = True
        
        # Remove above flag
        if not self._apply_wmctrl_flag(window_id, "remove", "above"):
            success = False
        
        # Add background flags
        self._apply_wmctrl_flag(window_id, "add", "skip_pager")
        self._apply_wmctrl_flag(window_id, "add", "below")
        
        return success
    
    def _apply_wmctrl_flag(self, window_id: str, operation: str, flag: str) -> bool:
        """Helper to apply single wmctrl flag"""
        try:
            subprocess.run(['wmctrl', '-i', '-r', window_id, '-b',
                          f'{operation},{flag}'],
                         capture_output=True, timeout=2)
            self.logger.debug(f"Applied wmctrl flag: {operation} {flag} to {window_id}")
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            self.logger.warning(f"Failed to apply flag {flag}: {e}")
            return False
    
    def close_window(self, window_id: str) -> bool:
        """Close window gracefully"""
        if not self.wmctrl_available:
            return False
        
        try:
            subprocess.run(['wmctrl', '-i', '-c', window_id],
                         capture_output=True, timeout=2)
            self.logger.debug(f"Closed window: {window_id}")
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            self.logger.warning(f"Failed to close window {window_id}: {e}")
            return False
    
    def wait_for_new_window(self, exclude_windows: List[str], 
                           max_attempts: int = 200) -> Optional[str]:
        """Wait for new window, excluding known ones - replaces bash wait_for_new_window"""
        for attempt in range(max_attempts):
            current_windows = self.find_engine_windows()
            
            # Look for window not in exclusion list
            for window_id in current_windows:
                if window_id not in exclude_windows:
                    self.logger.success(f"New window detected: {window_id}")
                    return window_id
            
            time.sleep(0.05)
        
        self.logger.error(f"Timeout waiting for new window after {max_attempts} attempts")
        return None


class ProcessManager:
    """Manages process lifecycle - replaces bash process management"""
    
    def __init__(self, logger: EngineLogger):
        self.logger = logger
    
    def is_running(self, pid: int) -> bool:
        """Check if process is running"""
        try:
            os.kill(pid, 0)  # Signal 0 doesn't kill, just checks
            return True
        except (OSError, ProcessLookupError):
            return False
    
    def kill_process(self, pid: int, signal: signal.Signals = signal.SIGTERM, 
                    max_attempts: int = 3) -> bool:
        """Kill process gracefully with escalating signals"""
        if not self.is_running(pid):
            self.logger.debug(f"Process {pid} not running")
            return True
        
        current_signal = signal
        for attempt in range(max_attempts):
            try:
                os.kill(pid, current_signal)
                self.logger.debug(f"Sent SIG{current_signal.name} to PID {pid}")
                
                time.sleep(0.3)
                
                if not self.is_running(pid):
                    self.logger.debug(f"Process {pid} killed successfully")
                    return True
                
                # Escalate signal
                current_signal = signal.SIGKILL
            except ProcessLookupError:
                return True
            except Exception as e:
                self.logger.warning(f"Error killing PID {pid}: {e}")
                return False
        
        self.logger.error(f"Failed to kill process {pid} after {max_attempts} attempts")
        return False
    
    def kill_by_pattern(self, pattern: str, signal_name: str = "TERM") -> bool:
        """Kill all processes matching pattern"""
        try:
            signal_num = getattr(signal, f"SIG{signal_name}")
            result = subprocess.run(['pkill', f'-{signal_num}', '-f', pattern],
                                  capture_output=True, timeout=5)
            self.logger.debug(f"Killed processes matching '{pattern}' with SIG{signal_name}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to kill pattern '{pattern}': {e}")
            return False


class EngineDetector:
    """Detects engine binary - replaces bash engine detection"""
    
    def __init__(self, logger: EngineLogger):
        self.logger = logger
    
    def detect_engine_binary(self) -> Optional[str]:
        """Find engine binary in PATH and common locations"""
        binaries = ["linux-wallpaperengine", "wallpaperengine"]
        
        # Check PATH
        for binary in binaries:
            result = subprocess.run(['which', binary],
                                  capture_output=True, 
                                  text=True)
            if result.returncode == 0:
                engine_path = result.stdout.strip()
                self.logger.success(f"Engine found in PATH: {engine_path}")
                return engine_path
        
        # Check common locations
        locations = [
            Path.home() / ".local/bin/linux-wallpaperengine",
            Path("/usr/local/bin/linux-wallpaperengine"),
            Path("/usr/bin/linux-wallpaperengine"),
            Path.home() / "linux-wallpaperengine/build/output/linux-wallpaperengine",
            Path.home() / "linux-wallpaperengine/build/linux-wallpaperengine",
        ]
        
        for location in locations:
            if location.is_file() and os.access(location, os.X_OK):
                engine_path = str(location)
                self.logger.success(f"Engine found at: {engine_path}")
                
                # Add to PATH
                bin_dir = str(location.parent)
                os.environ['PATH'] = f"{bin_dir}:{os.environ['PATH']}"
                return engine_path
        
        self.logger.error("Engine not found in PATH or common locations")
        return None


class EngineStateManager:
    """Manages engine state persistence - replaces bash state management"""
    
    def __init__(self, logger: EngineLogger):
        self.logger = logger
        self.data_dir = Path.home() / ".local/share/linux-wallpaper-engine-features"
        self.state_file = self.data_dir / "engine.state"
        self.engines_running_file = self.data_dir / "engines_running"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._init_state()
    
    def _init_state(self):
        """Initialize state file if missing"""
        if not self.state_file.exists():
            initial_state = {
                "last_pid": None,
                "last_windows": [],
                "last_wallpaper": None,
                "last_execution": None
            }
            self._write_state(initial_state)
            self.logger.success(f"Initialized state file: {self.state_file}")
    
    def save_state(self, pid: int, windows: List[str] = None, 
                   wallpaper: str = ""):
        """Save current engine state"""
        state = {
            "last_pid": pid,
            "last_windows": windows or [],
            "last_wallpaper": wallpaper,
            "last_execution": datetime.utcnow().isoformat() + "Z"
        }
        self._write_state(state)
        self.logger.debug(f"State saved: PID={pid}, Windows={len(windows or [])} items")
    
    def _write_state(self, state: dict):
        """Write state to JSON file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to write state: {e}")
    
    def _read_state(self) -> dict:
        """Read state from JSON file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to read state: {e}")
        
        return self._get_default_state()
    
    @staticmethod
    def _get_default_state() -> dict:
        return {
            "last_pid": None,
            "last_windows": [],
            "last_wallpaper": None,
            "last_execution": None
        }
    
    def get_last_pid(self) -> Optional[int]:
        """Get last engine PID"""
        return self._read_state().get("last_pid")
    
    def get_last_windows(self) -> List[str]:
        """Get last engine windows"""
        return self._read_state().get("last_windows", [])
    
    def track_engine(self, pid: int, wallpaper: str = ""):
        """Track engine in running list"""
        entry = f"{pid}:{wallpaper}:{int(time.time())}"
        
        try:
            with open(self.engines_running_file, 'a') as f:
                f.write(entry + '\n')
            
            # Keep only last 100 entries
            self._trim_running_file(100)
            self.logger.debug(f"Tracked engine: PID={pid}")
        except Exception as e:
            self.logger.warning(f"Failed to track engine: {e}")
    
    def _trim_running_file(self, max_entries: int):
        """Keep only last N entries in running file"""
        try:
            with open(self.engines_running_file, 'r') as f:
                lines = f.readlines()
            
            if len(lines) > max_entries:
                with open(self.engines_running_file, 'w') as f:
                    f.writelines(lines[-max_entries:])
        except Exception as e:
            self.logger.warning(f"Failed to trim running file: {e}")
    
    def cleanup(self, max_age_days: int = 7):
        """Clean up old logs and state"""
        max_age_seconds = max_age_days * 86400
        now = time.time()
        
        # Check log file age
        log_file = Path(EngineLogger._get_default_log_file())
        if log_file.exists():
            file_age = now - log_file.stat().st_mtime
            if file_age > max_age_seconds:
                log_file.unlink()
                self.logger.success("Cleaned up old log file")
        
        # Keep only last 50 entries in running file
        self._trim_running_file(50)


class EnvironmentManager:
    """Manages X11 and D-Bus environment setup - replaces bash environment setup"""
    
    def __init__(self, logger: EngineLogger):
        self.logger = logger
    
    def setup_x11(self):
        """Setup X11 environment variables"""
        # Set DISPLAY
        if not os.environ.get('DISPLAY'):
            # Try to extract from running processes
            display = self._find_display_from_processes()
            if not display:
                display = ":0"
            os.environ['DISPLAY'] = display
            self.logger.debug(f"Set DISPLAY={display}")
        
        # Set XAUTHORITY
        if not os.environ.get('XAUTHORITY'):
            xauth = self._find_xauthority()
            if xauth:
                os.environ['XAUTHORITY'] = xauth
                self.logger.debug(f"Set XAUTHORITY={xauth}")
    
    def setup_dbus(self):
        """Setup D-Bus environment"""
        if not os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
            uid = os.getuid()
            bus_path = f"/run/user/{uid}/bus"
            if Path(bus_path).exists():
                os.environ['DBUS_SESSION_BUS_ADDRESS'] = f"unix:path={bus_path}"
                self.logger.debug("Set DBUS_SESSION_BUS_ADDRESS")
    
    def setup_all(self):
        """Setup all environments"""
        self.setup_x11()
        self.setup_dbus()
        self.logger.success("Environment setup complete")
    
    @staticmethod
    def _find_display_from_processes() -> Optional[str]:
        """Extract DISPLAY from running X11 processes"""
        try:
            uid = os.getuid()
            result = subprocess.run(
                ['pgrep', '-u', str(uid), '-f', '^/usr/bin/X'],
                capture_output=True, text=True, timeout=2
            )
            
            for pid_str in result.stdout.strip().split('\n'):
                if pid_str:
                    try:
                        with open(f"/proc/{pid_str}/environ", 'rb') as f:
                            environ = f.read().decode('utf-8', errors='ignore')
                            for var in environ.split('\0'):
                                if var.startswith('DISPLAY='):
                                    return var.split('=')[1]
                    except Exception:
                        continue
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _find_xauthority() -> Optional[str]:
        """Find XAUTHORITY file"""
        default = str(Path.home() / ".Xauthority")
        
        try:
            uid = os.getuid()
            result = subprocess.run(
                ['pgrep', '-u', str(uid)],
                capture_output=True, text=True, timeout=2
            )
            
            for pid_str in result.stdout.strip().split('\n')[:5]:
                if pid_str:
                    try:
                        with open(f"/proc/{pid_str}/environ", 'rb') as f:
                            environ = f.read().decode('utf-8', errors='ignore')
                            for var in environ.split('\0'):
                                if var.startswith('XAUTHORITY='):
                                    xauth = var.split('=')[1]
                                    if Path(xauth).exists():
                                        return xauth
                    except Exception:
                        continue
        except Exception:
            pass
        
        return default if Path(default).exists() else None


class EngineOrchestrator:
    """High-level engine orchestration - coordinates all utilities"""
    
    def __init__(self):
        self.logger = EngineLogger()
        self.window_manager = WindowManager(self.logger)
        self.process_manager = ProcessManager(self.logger)
        self.engine_detector = EngineDetector(self.logger)
        self.state_manager = EngineStateManager(self.logger)
        self.env_manager = EnvironmentManager(self.logger)
        
        self.engine_path: Optional[str] = None
    
    def initialize(self) -> bool:
        """Initialize orchestrator"""
        self.logger.success("Initializing engine orchestrator")
        
        # Setup environment
        self.env_manager.setup_all()
        
        # Detect engine
        self.engine_path = self.engine_detector.detect_engine_binary()
        if not self.engine_path:
            self.logger.error("Cannot continue without engine binary")
            return False
        
        return True
    
    def apply_wallpaper(self, wallpaper_path: str, remove_above: bool = False) -> bool:
        """Apply wallpaper - main operation"""
        self.logger.info(f"Applying wallpaper: {wallpaper_path}")
        
        # Get current windows
        old_windows = self.window_manager.find_engine_windows()
        self.logger.debug(f"Old windows: {old_windows}")
        
        # Get active window
        try:
            active_window = subprocess.run(['xdotool', 'getactivewindow'],
                                         capture_output=True, 
                                         text=True, 
                                         timeout=2).stdout.strip()
        except Exception:
            active_window = None
        
        # Launch engine
        try:
            process = subprocess.Popen(
                [self.engine_path, wallpaper_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            engine_pid = process.pid
            self.logger.success(f"Engine launched with PID {engine_pid}")
        except Exception as e:
            self.logger.error(f"Failed to launch engine: {e}")
            return False
        
        # Start monitor thread if needed
        if remove_above:
            monitor_thread = threading.Thread(
                target=self._monitor_and_fix_windows,
                args=(engine_pid, old_windows),
                daemon=True
            )
            monitor_thread.start()
        
        # Wait for new window
        new_window = self.window_manager.wait_for_new_window(old_windows)
        if not new_window:
            self.logger.error("No window found for new engine")
            return False
        
        self.logger.success(f"New window ready: {new_window}")
        
        # Apply flags
        if remove_above:
            self.window_manager.apply_background_flags(new_window)
        
        # Restore focus
        if active_window:
            try:
                subprocess.run(['xdotool', 'windowactivate', active_window],
                             timeout=2)
            except Exception:
                pass
        
        # Close old windows
        for old_win in old_windows:
            if old_win != new_window:
                self.window_manager.close_window(old_win)
        
        # Save state
        self.state_manager.save_state(engine_pid, [new_window], wallpaper_path)
        
        self.logger.success("Wallpaper applied successfully")
        return True
    
    def _monitor_and_fix_windows(self, engine_pid: int, exclude_windows: List[str],
                                max_duration: int = 300):
        """Background monitor to continuously apply window flags"""
        start_time = time.time()
        
        while time.time() - start_time < max_duration:
            if not self.process_manager.is_running(engine_pid):
                break
            
            windows = self.window_manager.find_engine_windows()
            for window in windows:
                if window not in exclude_windows:
                    self.window_manager.apply_background_flags(window)
            
            time.sleep(0.5)
    
    def stop_engine(self):
        """Stop all engine processes"""
        self.logger.info("Stopping all engine processes")
        
        # Kill by pattern
        self.process_manager.kill_by_pattern("linux-wallpaperengine", "KILL")
        
        # Clear state
        self.state_manager.save_state(None)
        
        self.logger.success("Engine stopped")


if __name__ == "__main__":
    # Example usage
    orchestrator = EngineOrchestrator()
    
    if orchestrator.initialize():
        orchestrator.apply_wallpaper(
            "/path/to/wallpaper",
            remove_above=True
        )
