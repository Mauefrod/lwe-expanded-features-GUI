"""Centralized logging utilities"""


class Logger:
    """Handles logging for all application components"""
    
    def __init__(self, callback=None):
        self.callback = callback
    
    def log(self, message, level="INFO"):
        """Log a message with optional level prefix"""
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
        formatted_msg = f"[{component_name}] {message}"
        self.log(formatted_msg, level)
    
    def _format_message(self, message, level):
        """Format message with level prefix"""
        if message.startswith("["):
            # Already has prefix
            return message
        return f"[{level}] {message}"
    
    def set_callback(self, callback):
        """Update the logging callback"""
        self.callback = callback


# Global logger instance
_global_logger = None


def get_logger():
    """Get or create global logger"""
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger()
    return _global_logger


def set_logger_callback(callback):
    """Set the callback for global logger"""
    get_logger().set_callback(callback)
