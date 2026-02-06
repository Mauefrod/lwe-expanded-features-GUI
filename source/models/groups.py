"""Wallpaper groups management"""

from os import path
from models.config import ConfigManager
from common.logger import get_logger


class GroupManager:
    """Manages wallpaper groups and favorites"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger()
    
    # ========== Favorites ==========
    def toggle_favorite(self, wallpaper_id):
        """Toggle favorite status for a wallpaper"""
        favs = self.config["--favorites"]
        
        if wallpaper_id in favs:
            favs.remove(wallpaper_id)
            self.logger.component("GROUPS", f"Removed {wallpaper_id} from favorites")
        else:
            favs.append(wallpaper_id)
            self.logger.component("GROUPS", f"Added {wallpaper_id} to favorites")
        
        ConfigManager.save(self.config)
    
    def is_favorite(self, wallpaper_id):
        """Check if wallpaper is favorite"""
        return wallpaper_id in self.config["--favorites"]
    
    # ========== Groups ==========
    def create_group(self, name):
        """Create a new group"""
        name = name.strip()
        if not name:
            self.logger.component("GROUPS", "Cannot create group with empty name", "WARNING")
            return False
        
        groups = self.config["--groups"]
        if name not in groups:
            groups[name] = []
            ConfigManager.save(self.config)
            self.logger.component("GROUPS", f"Created group '{name}'")
            return True
        
        self.logger.component("GROUPS", f"Group '{name}' already exists", "WARNING")
        return False
    
    def add_to_group(self, group, wallpaper_id):
        """Add wallpaper to group"""
        groups = self.config["--groups"]
        if group not in groups:
            groups[group] = []
        
        wallpaper_id = str(wallpaper_id)
        if wallpaper_id not in groups[group]:
            groups[group].append(wallpaper_id)
            ConfigManager.save(self.config)
            self.logger.component("GROUPS", f"Added {wallpaper_id} to group '{group}'")
        else:
            self.logger.component("GROUPS", f"{wallpaper_id} already in group '{group}'", "WARNING")
    
    def remove_from_group(self, group, wallpaper_id):
        """Remove wallpaper from group"""
        groups = self.config["--groups"]
        wallpaper_id = str(wallpaper_id)
        
        if group in groups and wallpaper_id in groups[group]:
            groups[group].remove(wallpaper_id)
            ConfigManager.save(self.config)
            self.logger.component("GROUPS", f"Removed {wallpaper_id} from group '{group}'")
        else:
            self.logger.component("GROUPS", f"{wallpaper_id} not found in group '{group}'", "WARNING")
    
    def in_group(self, group, wallpaper_id):
        """Check if wallpaper is in group"""
        return str(wallpaper_id) in self.config["--groups"].get(group, [])
    
    def delete_group(self, group_id):
        """Delete a group"""
        if group_id in self.config["--groups"]:
            del self.config["--groups"][group_id]
            ConfigManager.save(self.config)
            self.logger.component("GROUPS", f"Deleted group '{group_id}'")
        else:
            self.logger.component("GROUPS", f"Group '{group_id}' not found", "WARNING")
    
    def get_all_groups(self):
        """Get all group names"""
        return list(self.config["--groups"].keys())
    
    def get_group_contents(self, group):
        """Get wallpapers in a group"""
        return self.config["--groups"].get(group, [])
    
    # ========== Not Working Group ==========
    def delete_not_working_wallpapers(self):
        """Delete wallpapers in 'not working' group from directory"""
        from shutil import rmtree
        
        wallpaper_dir = self.config.get("--dir")
        not_working_list = self.config.get("--groups", {}).get("not working", [])
        
        if not wallpaper_dir:
            self.logger.component("GROUPS", "No wallpaper directory configured", "WARNING")
            return
        
        if not not_working_list:
            self.logger.component("GROUPS", "No wallpapers in 'not working' group")
            return
        
        self.logger.component("GROUPS", 
                            f"Starting deletion of {len(not_working_list)} wallpapers from 'not working' group")
        
        deleted_count = 0
        for wallpaper_id in not_working_list:
            wallpaper_path = path.join(wallpaper_dir, str(wallpaper_id))
            
            if path.exists(wallpaper_path) and path.isdir(wallpaper_path):
                try:
                    rmtree(wallpaper_path)
                    deleted_count += 1
                    self.logger.component("GROUPS", f"Deleted wallpaper: {wallpaper_id}")
                except Exception as e:
                    self.logger.component("GROUPS", f"Error deleting wallpaper {wallpaper_id}: {e}", "ERROR")
            else:
                self.logger.component("GROUPS", f"Wallpaper not found: {wallpaper_id}", "WARNING")
        
        # Clean up group after deletion
        self.config["--groups"]["not working"] = []
        ConfigManager.save(self.config)
        self.logger.component("GROUPS", 
                            f"Deletion complete: {deleted_count}/{len(not_working_list)} wallpapers deleted")
