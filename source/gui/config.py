"""
Backward compatibility wrapper for configuration management.
Actual implementation now in models.config and services.argument_builder
"""
from models.config import (
    DEFAULT_CONFIG,
    ConfigManager,
    ConfigValidator,
    ConfigUpdater
)
from common.constants import RESOLUTIONS, CONFIG_PATH
from common.validators import validate_directory
from services.argument_builder import ArgumentBuilder


# Re-export for backward compatibility
__all__ = [
    'DEFAULT_CONFIG',
    'CONFIG_PATH',
    'RESOLUTIONS',
    'load_config',
    'save_config',
    'merge_config',
    'validate_directory',
    'build_args',
    'update_set_flag'
]


# Backward compatible function wrappers
def load_config():
    """Backward compatibility wrapper"""
    return ConfigManager.load()


def save_config(config):
    """Backward compatibility wrapper"""
    ConfigManager.save(config)


def merge_config(defaults, loaded):
    """Backward compatibility wrapper"""
    ConfigManager.merge(defaults, loaded)


def build_args(config, log_callback=None, show_gui_warning=False):
    """Backward compatibility wrapper"""
    builder = ArgumentBuilder(config, log_callback, show_gui_warning)
    return builder.build_arguments()


def update_set_flag(config):
    """Backward compatibility wrapper"""
    ConfigUpdater.update_set_flag(config)
