"""Wallpaper loading and management service"""

from PIL import Image, ImageTk
from os import path, listdir

from common.constants import THUMB_SIZE, THUMB_DESIRED_COLUMNS, THUMB_MIN_WIDTH, THUMB_ASPECT_RATIO


def calculate_dynamic_thumb_size(screen_width, desired_columns=THUMB_DESIRED_COLUMNS):
    """
    Calculate thumbnail size dynamically based on screen width.
    
    Args:
        screen_width: Screen width in pixels
        desired_columns: Target number of columns
    
    Returns:
        tuple: (width, height)
    """
    padding_per_thumb = 40
    available_width = screen_width - (padding_per_thumb * desired_columns)
    thumb_width = max(THUMB_MIN_WIDTH, available_width // desired_columns)
    thumb_height = int(thumb_width * THUMB_ASPECT_RATIO)
    return (thumb_width, thumb_height)


class WallpaperLoader:
    """Manages wallpaper preview caching and loading"""
    
    def __init__(self):
        self.preview_cache = {}
    
    def load_preview(self, wallpaper_folder):
        """
        Load wallpaper preview image
        
        Args:
            wallpaper_folder: Path to wallpaper directory
        
        Returns:
            PhotoImage or None: The preview image or None if not found
        """
        if wallpaper_folder in self.preview_cache:
            return self.preview_cache[wallpaper_folder][1]
        
        for name in ("preview.jpg", "preview.png", "preview.gif"):
            full_path = path.join(wallpaper_folder, name)
            if path.exists(full_path):
                try:
                    img = Image.open(full_path)
                    img.thumbnail(THUMB_SIZE)
                    tk_img = ImageTk.PhotoImage(image=img)
                    # Store both PIL Image and PhotoImage to prevent garbage collection
                    self.preview_cache[wallpaper_folder] = (img, tk_img)
                    return tk_img
                except Exception as e:
                    print(f"[WARNING] Error loading preview {full_path}: {e}")
                    continue
        
        return None
    
    def clear_cache(self):
        """Clear the preview cache"""
        self.preview_cache.clear()


class WallpaperFinder:
    """Finds and counts wallpapers"""
    
    @staticmethod
    def count_all(root_dir, loader):
        """Count all wallpapers with previews"""
        if not root_dir or not path.exists(root_dir) or not path.isdir(root_dir):
            return 0
        try:
            count = 0
            for w in listdir(root_dir):
                folder = path.join(root_dir, w)
                if not path.isdir(folder):
                    continue
                if loader.load_preview(folder):
                    count += 1
            return count
        except (OSError, PermissionError):
            return 0
    
    @staticmethod
    def count_favorites(root_dir, favorites, loader):
        """Count favorite wallpapers with previews"""
        if not root_dir or not path.exists(root_dir) or not path.isdir(root_dir):
            return 0
        try:
            favs = set(favorites)
            count = 0
            for w in listdir(root_dir):
                folder = path.join(root_dir, w)
                if not path.isdir(folder):
                    continue
                if w in favs and loader.load_preview(folder):
                    count += 1
            return count
        except (OSError, PermissionError):
            return 0
    
    @staticmethod
    def get_wallpapers_list(root_dir, loader, group=None, favorites=None, groups_dict=None):
        """
        Get list of wallpapers matching criteria
        
        Args:
            root_dir: Root wallpaper directory
            loader: WallpaperLoader instance
            group: Optional group name filter
            favorites: Optional favorites list
            groups_dict: Optional groups dictionary
        
        Returns:
            list: Filtered wallpaper list
        """
        if not root_dir or not path.exists(root_dir) or not path.isdir(root_dir):
            return []
        
        try:
            wallpapers = []
            
            for w in listdir(root_dir):
                folder = path.join(root_dir, w)
                if not path.isdir(folder):
                    continue
                
                if not loader.load_preview(folder):
                    continue
                
                # Apply group filter
                if group and groups_dict:
                    if not WallpaperFinder._is_in_group(w, group, groups_dict):
                        continue
                
                wallpapers.append(w)
            
            return wallpapers
        
        except (OSError, PermissionError):
            return []
    
    @staticmethod
    def _is_in_group(wallpaper_id, group, groups_dict):
        """Check if wallpaper is in group"""
        if group not in groups_dict:
            return False
        return str(wallpaper_id) in groups_dict[group]
