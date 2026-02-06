"""Validators for common operations"""

import os
from os import path


def validate_directory(dir_path, log_callback=None):
    """
    Validate that directory exists and is accessible.
    
    Args:
        dir_path: Path to validate
        log_callback: Optional logging callback
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not dir_path:
        return False, "No directory path specified"
    
    if not path.exists(dir_path):
        error_msg = f"Directory does not exist: {dir_path}"
        if log_callback:
            log_callback(f"[WARNING] {error_msg}")
        return False, error_msg
    
    if not path.isdir(dir_path):
        error_msg = f"Path is not a directory: {dir_path}"
        if log_callback:
            log_callback(f"[WARNING] {error_msg}")
        return False, error_msg
    
    # Check read permissions
    if not os.access(dir_path, os.R_OK):
        error_msg = f"Directory is not readable: {dir_path}"
        if log_callback:
            log_callback(f"[WARNING] {error_msg}")
        return False, error_msg
    
    return True, None


def is_valid_directory_path(dir_path):
    """Simple check without logging"""
    is_valid, _ = validate_directory(dir_path)
    return is_valid


def validate_timer_value(timer_str):
    """
    Validate timer value is a valid integer.
    
    Args:
        timer_str: Timer value as string
    
    Returns:
        tuple: (is_valid: bool, value: int or None)
    """
    try:
        value = int(timer_str)
        if value > 0:
            return True, value
        return False, None
    except (ValueError, TypeError):
        return False, None


def validate_resolution(resolution):
    """
    Validate resolution format (e.g., '0x0x1920x1080').
    
    Args:
        resolution: Resolution string
    
    Returns:
        bool: True if valid format
    """
    if not isinstance(resolution, str):
        return False
    
    parts = resolution.split('x')
    if len(parts) != 4:
        return False
    
    try:
        for part in parts:
            int(part)
        return True
    except ValueError:
        return False
