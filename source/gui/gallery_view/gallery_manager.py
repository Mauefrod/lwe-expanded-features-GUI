from os import path
from gui.wallpaper_loader import count_all_wallpapers, count_favorite_wallpapers, get_wallpapers_list


class GalleryManager:
    """Manages gallery state and rendering logic for wallpapers and groups"""

    def __init__(self, gallery_view, loader, config):
        self.gallery_view = gallery_view
        self.loader = loader
        self.config = config
        # Use the group manager from gallery_view
        self.group_manager = gallery_view.group_manager

    def refresh(self) -> None:
        """Refresh complete gallery display based on current view state"""
        self.gallery_view.clear_gallery()

        root_dir = self.config["--dir"]

        if not root_dir or not path.exists(root_dir) or not path.isdir(root_dir):
            self.gallery_view.item_list = []
            return

        if self.gallery_view.current_view == "groups":
            self._render_groups_view(root_dir)
        else:
            self._render_wallpapers_view(root_dir)

    def _render_groups_view(self, root_dir: str) -> None:
        """Render the groups view showing all wallpaper groups"""

        groups = self.group_manager.get_all_groups()
        self.gallery_view.item_list = ["__ALL__", "__FAVORITES__"] + groups + ["__NEW_GROUP__"]


        for index, group_id in enumerate(self.gallery_view.item_list):
            row = index // self.gallery_view.max_cols
            col = index % self.gallery_view.max_cols

            if group_id == "__NEW_GROUP__":
                self.gallery_view.create_new_group_thumbnail(index, row, col)

            elif group_id == "__ALL__":
                count = count_all_wallpapers(root_dir, self.loader)
                self.gallery_view.create_group_thumbnail(
                    index, row, col, group_id, "All wallpapers", count
                )

            elif group_id == "__FAVORITES__":
                count = count_favorite_wallpapers(
                    root_dir, self.config["--favorites"], self.loader
                )
                self.gallery_view.create_group_thumbnail(
                    index, row, col, group_id, "Favorites", count
                )

            else:
                count = len(self.group_manager.get_group_contents(group_id))
                self.gallery_view.create_group_thumbnail(
                    index, row, col, group_id, group_id, count
                )

    def _render_wallpapers_view(self, root_dir: str) -> None:
        """Render the wallpapers view showing thumbnails for selected group or all"""

        wallpapers = get_wallpapers_list(
            root_dir,
            self.loader,
            self.gallery_view.current_group,
            self.config["--favorites"],
            self.config["--groups"]
        )
        self.gallery_view.item_list = wallpapers


        for index, wallpaper_id in enumerate(wallpapers):
            row = index // self.gallery_view.max_cols
            col = index % self.gallery_view.max_cols

            folder = path.join(root_dir, wallpaper_id)
            img = self.loader.load_preview(folder)

            if img:
                self.gallery_view.create_wallpaper_thumbnail(
                    index, row, col, wallpaper_id, img
                )