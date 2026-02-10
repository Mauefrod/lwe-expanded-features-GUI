"""
Backward compatibility wrapper for group management.
Actual implementation now in models.groups
As you may imagine at this point, this is a wrapper, and works SOLELY as an astraction layer
If you want to add features or change the way groups are managed, override the functions in the actual codebase
"""
from models.groups import GroupManager
from common.logger import set_logger_callback



_group_manager = None


def set_log_callback(callback):
    """Configure the global logging callback"""
    set_logger_callback(callback)


def toggle_favorite(config, wallpaper_id):
    """Backward compatibility wrapper"""
    manager = GroupManager(config)
    manager.toggle_favorite(wallpaper_id)


def is_favorite(config, wallpaper_id):
    """Backward compatibility wrapper"""
    manager = GroupManager(config)
    return manager.is_favorite(wallpaper_id)


def create_group(config, name):
    """Backward compatibility wrapper"""
    manager = GroupManager(config)
    return manager.create_group(name)


def add_to_group(config, group, wallpaper_id):
    """Backward compatibility wrapper"""
    manager = GroupManager(config)
    manager.add_to_group(group, wallpaper_id)


def remove_from_group(config, group, wallpaper_id):
    """Backward compatibility wrapper"""
    manager = GroupManager(config)
    manager.remove_from_group(group, wallpaper_id)


def in_group(config, group, wallpaper_id):
    """Backward compatibility wrapper"""
    manager = GroupManager(config)
    return manager.in_group(group, wallpaper_id)


def delete_group(config, group_id):
    """Backward compatibility wrapper"""
    manager = GroupManager(config)
    manager.delete_group(group_id)


def delete_not_working_wallpapers(config):
    """Backward compatibility wrapper"""
    manager = GroupManager(config)
    manager.delete_not_working_wallpapers()
