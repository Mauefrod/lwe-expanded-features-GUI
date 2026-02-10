"""Centralized logging utilities"""


class Logger:
    """Handles logging for all application components"""

    def __init__(self, callback=None):
        self.callback = callback

    def log(self, message, level="INFO"):
        """Log a message with optional level prefix"""
        """level: string - INFO, WARNING, ERROR, DEBUG"""
        """message: pretty self explanatory, to avoid weird behavior, avoid starting with [], use ([]) or {[]}"""
        """YOU OUTGHT TO RESERVE [] FOR EITHER LEVEL OR COMPONENT PREFIXES, that being said, the way to log a new
        component or level is via the component and level functions, so you don't have to worry about it at all, 
        just don't start your messages with [ and you are good to go =)."""
        formatted = self._format_message(message, level)
        if self.callback:
            self.callback(formatted)
        else:
            print(formatted)

    def info(self, message):
        """Log info level message"""
        self.log(message, "INFO")

    def warning(self, message):
        """Log warning level message"""
        self.log(message, "WARNING")

    def error(self, message):
        """Log error level message"""
        self.log(message, "ERROR")

    def debug(self, message):
        """Log debug level message"""
        self.log(message, "DEBUG")

    def component(self, component_name, message, level="INFO"):
        """Log message from a specific component"""
        """component_name: string - name of the component (e.g. 'CONFIG', 'ENGINE', 'GUI')"""
        """Logs created by the Engine are not bugs to this scope, refer to the linux-wallpaperengine github"""
        formatted_msg = f"[{component_name}] {message}"
        self.log(formatted_msg, level)

    def _format_message(self, message, level):
        """Format message with level prefix"""
        """This function should prevent edge-cases with messages starting with [, that being said, I believe in Murphy's law,
        so it's likely to not work at all =)"""
        if message.startswith("["):

            return message
        return f"[{level}] {message}"

    def set_callback(self, callback):
        """Update the logging callback"""
        self.callback = callback



_global_logger = None # Singleton pattern (having 2 loggers would be weird)


def get_logger():
    """Get or create global logger"""
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger()
    return _global_logger


def set_logger_callback(callback):
    """Set the callback for global logger"""
    get_logger().set_callback(callback)
