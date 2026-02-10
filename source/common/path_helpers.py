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
    env variables:
        LWE_SCRIPT_DIR: Optional environment variable to specify script directory
    Search order:
        1. LWE_SCRIPT_DIR environment variable
        2. Relative to this module (common)
        3. Relative to current working directory (source/core)
    Debug:
        If the script cannot be found, just clone the repo again, this is not a reproducible issue and should not happen.
    """
    script_dir = os.getenv('LWE_SCRIPT_DIR')
    if script_dir:
        script_path = path.join(script_dir, script_name)
        if path.exists(script_path):
            return script_path

    module_dir = path.dirname(path.dirname(path.abspath(__file__)))
    relative_path = path.join(module_dir, 'core', script_name)
    if path.exists(relative_path):
        return relative_path

    cwd_path = path.join(os.getcwd(), 'source', 'core', script_name)
    if path.exists(cwd_path):
        return cwd_path

    raise FileNotFoundError(
        f"Cannot locate script '{script_name}'. "
        f"Searched paths:\n"
        f"  - LWE_SCRIPT_DIR env var\n"
        f"  - Module relative: {relative_path}\n"
        f"  - CWD relative: {cwd_path}"
        f"Edge case: if you are not running the app from neither GUI.py, run.sh or the dekstop file," 
        f"I honestly don't know how you managed to do it.\n I won't provide debbuging tips for this," 
        f"maybe you can work around it via the LWE_SCRIPT_DIR env variable, but if you are doing something"
        f"like this, you probably know what you are doing and can figure it out on your own =)"
    )


def expand_user_path(path_str):
    """
    Expand user home directory in path.
    
    Args:
        path_str: Path string with ~ notation
    
    Returns:
        str: Expanded path
    Documentation:
        This function is merely a wrapper, if you need to implement something else, you should consider
        implementing it by yourself. 
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
