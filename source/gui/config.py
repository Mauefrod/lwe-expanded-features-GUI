"""
As you can see, all comments are "backward compatibility wrapper", in the scenario
Of it not being clear enough, THIS IS A WRAPPER, override the functions in the actual codebase,
If you Hardcode values / functions in here, I will find you. 
"""
from models.config import (
    DEFAULT_CONFIG,
    ConfigManager,
    ConfigValidator, # legacy, use common.validators. Won't be removed, but don't implement features based on it.
    ConfigUpdater
)
from common.constants import RESOLUTIONS, CONFIG_PATH
from common.validators import validate_directory
from services.argument_builder import ArgumentBuilder


# API used accross multiple modules. Don't ask me why i underscored it... 
# Naming Convention? WTF is that. 
# I guess the point is it's private to the scope of this module, but public for the project
# Anyways... i dunno, good luck =)

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
