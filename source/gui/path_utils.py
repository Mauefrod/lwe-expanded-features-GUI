"""
Backward compatibility wrapper for path utilities.
Imports now handled by common.path_helpers module.
"""
from common.path_helpers import get_script_path

__all__ = ['get_script_path']
