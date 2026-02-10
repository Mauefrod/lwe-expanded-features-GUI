"""Wallpaper groups management"""
"""This is the actual implementation (not legacy), any changes or features must go here."""
"""I think all of this logic is pretty self explanatory, but if in doub:
- Favorites are just a special group, they are handled separately for ease of access and performance reasons, 
but they could be easily merged with the rest of the groups if needed. It exists by default in the GUI.

- Not working group is just a special group that is meant to be used as a staging area for wallpapers that are not working,
they will be removed upon runtime.

- One of the most interesting features that could be added in here is to "speciallize" groups as playlists, that way you could
set wallpapers in order (not random), but you would need to either refactor the -delay flag (in main.sh) or add a new one 
(recommended if you want to avoid spagetthi code).

- Another interesting feature would be to use the tagging system from the project.json that comes with every wallpaper,
it's something I'm currently working on with my paperCore Module (Repo), so far it's private, but if you want to contribute,
open an issue and I will allow you to fork it

- You can also implement a "blacklist" group that would be the opposite of the "not working" group, that way you could have a 
staging area for wallpapers that are working but you don't want to use for some reason, maybe they are too resource intensive,
or you just don't like them. That being said, the -random mode currently works via "pools" (refer to the main.sh documentation)
so you can just create a group called "blacklist" in the config.json as a standard group and then remove it from the pool.

- The main issue that needs work to be done here is the persistance of "not working" wallpapers (mainly when accessing 
WallpaperEngine (not the linux-one) since it will download the wallpapers again), not hard, but out of the current version 
scope.
"""
from os import path
from models.config import ConfigManager
from common.logger import get_logger


class GroupManager:
    """Manages wallpaper groups and favorites"""

    def __init__(self, config):
        self.config = config
        self.logger = get_logger()


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


        self.config["--groups"]["not working"] = []
        ConfigManager.save(self.config)
        self.logger.component("GROUPS",
                            f"Deletion complete: {deleted_count}/{len(not_working_list)} wallpapers deleted")
