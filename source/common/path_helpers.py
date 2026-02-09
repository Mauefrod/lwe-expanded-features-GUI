"""Path resolution helpers"""

import os
from os import path


def get_script_path(script_name):
    """
    Resolve path to a backend script.
    
    Args:
        script_name: Name of the script (e.g., 'main.sh')
    
    Returns:
        str: Full path to the script
    
    Raises:
        FileNotFoundError: If script cannot be found
    """
    # Try to get from environment variable first
    script_dir = os.getenv('LWE_SCRIPT_DIR')
    if script_dir:
        script_path = path.join(script_dir, script_name)
        if path.exists(script_path):
            return script_path
    
    # Try relative path from current module location
    module_dir = path.dirname(path.dirname(path.abspath(__file__)))
    relative_path = path.join(module_dir, 'core', script_name)
    if path.exists(relative_path):
        return relative_path
    
    # Try relative path from current working directory
    cwd_path = path.join(path.getcwd(), 'source', 'core', script_name)
    if path.exists(cwd_path):
        return cwd_path
    
    raise FileNotFoundError(
        f"Cannot locate script '{script_name}'. "
        f"Searched paths:\n"
        f"  - LWE_SCRIPT_DIR env var\n"
        f"  - Module relative: {relative_path}\n"
        f"  - CWD relative: {cwd_path}"
    )


def expand_user_path(path_str):
    """
    Expand user home directory in path.
    
    Args:
        path_str: Path string with ~ notation
    
    Returns:
        str: Expanded path
    """
    if path_str:
        return path.expanduser(path_str)
    return path_str


def normalize_path(path_str):
    """
    Normalize and expand a path.
    
    Args:
        path_str: Path to normalize
    
    Returns:
        str: Normalized absolute path
    """
    if not path_str:
        return path_str
    
    expanded = expand_user_path(path_str)
    return path.abspath(expanded)
