"""
Backward compatibility wrapper for wallpaper loading.
Actual implementation now in services.wallpaper_service
"""
from services.wallpaper_service import (
    WallpaperLoader,
    WallpaperFinder,
    calculate_dynamic_thumb_size
)
from common.constants import THUMB_SIZE

__all__ = [
    'WallpaperLoader',
    'WallpaperFinder',
    'calculate_dynamic_thumb_size',
    'THUMB_SIZE',
    'count_all_wallpapers',
    'count_favorite_wallpapers',
    'get_wallpapers_list'
]


# Backward compatible function wrappers
def count_all_wallpapers(root_dir, loader):
    """Backward compatibility wrapper"""
    return WallpaperFinder.count_all(root_dir, loader)


def count_favorite_wallpapers(root_dir, favorites, loader):
    """Backward compatibility wrapper"""
    return WallpaperFinder.count_favorites(root_dir, favorites, loader)


def get_wallpapers_list(root_dir, loader, group=None, favorites=None, groups_dict=None):
    """Backward compatibility wrapper"""
    return WallpaperFinder.get_wallpapers_list(
        root_dir, loader, group=group, favorites=favorites, groups_dict=groups_dict
    )