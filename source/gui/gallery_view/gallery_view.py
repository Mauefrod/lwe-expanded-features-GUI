from common.constants import THUMB_SIZE
from gui.gallery_view.thumbnails import ThumbnailFactory
from gui.gallery_view.context_menus import ContextMenuManager
from gui.gallery_view.dialogs import DialogManager
from models.groups import GroupManager


class GalleryView:
    """Manages gallery display for wallpapers and groups"""

    def __init__(self, canvas, inner_frame, config, loader, log_callback=None, group_manager=None):
        self.canvas = canvas
        self.inner_frame = inner_frame
        self.config = config
        self.loader = loader
        self.log_callback = log_callback
        # Use injected group manager or create one
        self.group_manager = group_manager or GroupManager(config)


        self.item_list = []
        self.thumbnail_widgets = {}
        self.current_view = "groups"
        self.current_group = None
        self.current_wallpaper = None


        self.max_cols = 6
        self.row_height = THUMB_SIZE[1] + 40


        self.thumbnails = ThumbnailFactory(inner_frame, config)
        self.context_menu_manager = ContextMenuManager(canvas, config, self.group_manager)
        self.dialog_manager = DialogManager(canvas, config, log_callback)


        self.on_wallpaper_applied = None # placeholders for event_handler for future implementation
        self.on_refresh_needed = None

    def log(self, message: str) -> None:
        """Send message to log callback"""
        if self.log_callback:
            self.log_callback(message)

    def clear_gallery(self) -> None:
        """Clear all gallery widgets from display"""
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.thumbnail_widgets = {}



    def create_group_thumbnail(self, index: int, row: int, col: int, group_id: str, name: str, count: int) -> None:
        """Create a group thumbnail widget"""
        frame = self.thumbnails.create_group_thumbnail(
            index, row, col, group_id, name, count,
            on_click=self.open_group,
            on_right_click=self._handle_group_right_click
        )
        self.thumbnail_widgets[index] = frame

    def create_new_group_thumbnail(self, index: int, row: int, col: int) -> None:
        """Create thumbnail button for creating a new group"""
        frame = self.thumbnails.create_new_group_thumbnail(
            index, row, col,
            on_click=self._handle_new_group_click
        )
        self.thumbnail_widgets[index] = frame

    def create_wallpaper_thumbnail(self, index: int, row: int, col: int, wallpaper_id: str, img) -> None:
        """Create a wallpaper thumbnail widget"""
        frame = self.thumbnails.create_wallpaper_thumbnail(
            index, row, col, wallpaper_id, img,
            current_wallpaper=self.current_wallpaper,
            on_double_click=self.apply_wallpaper,
            on_right_click=self._handle_wallpaper_right_click
        )
        self.thumbnail_widgets[index] = frame
        print(f"[GalleryView] Created thumbnail for wallpaper '{wallpaper_id}' at index {index} (row {row}, col {col})")



    def apply_wallpaper(self, wallpaper_id: str) -> None:
        """Apply selected wallpaper (double click handler)"""
        self.current_wallpaper = wallpaper_id
        self.log(f"[GUI] Applying wallpaper: {wallpaper_id}")
        if self.on_wallpaper_applied:
            self.on_wallpaper_applied(wallpaper_id)



    def open_group(self, group_id: str) -> None:
        """Open a group to display its wallpapers"""
        self.current_view = "wallpapers"
        self.current_group = group_id
        self._trigger_refresh()

    def go_back(self):
        """Return to the groups view"""
        self.current_view = "groups"
        self.current_group = None
        self._trigger_refresh()



    def _handle_wallpaper_right_click(self, event, wallpaper_id):
        """Handle right-click context menu on a wallpaper thumbnail"""
        callbacks = {
            'on_toggle_favorite': self._toggle_favorite_and_refresh,
            'on_assign_groups': self._show_assign_groups_dialog,
            'on_add_to_group': self._add_to_group_and_refresh,
            'on_mark_not_working': self._toggle_not_working_and_refresh
        }
        self.context_menu_manager.show_wallpaper_menu(event, wallpaper_id, callbacks)

    def _handle_group_right_click(self, event, group_id):
        """Handle right-click context menu on a group"""
        self.context_menu_manager.show_group_menu(
            event, group_id,
            on_delete=self._delete_group_and_refresh
        )

    def _handle_new_group_click(self):
        """Handle click on the new group creation button"""
        self.dialog_manager.show_new_group_dialog(
            on_created=self.on_refresh_needed
        )



    def _trigger_refresh(self) -> None:
        """Helper to trigger gallery refresh if callback is set"""
        if self.on_refresh_needed:
            self.on_refresh_needed()

    def _toggle_favorite_and_refresh(self, wallpaper_id):
        """Toggle wallpaper favorite status and refresh gallery display"""
        self.group_manager.toggle_favorite(wallpaper_id)
        self._trigger_refresh()

    def _toggle_not_working_and_refresh(self, wallpaper_id):
        """Toggle wallpaper 'not working' status and refresh gallery display"""
        if self.group_manager.in_group("not working", wallpaper_id):
            self.group_manager.remove_from_group("not working", wallpaper_id)
            self.log(f"[GUI] Removed {wallpaper_id} from 'not working'")
        else:
            self.group_manager.add_to_group("not working", wallpaper_id)
            self.log(f"[GUI] Added {wallpaper_id} to 'not working'")
        self._trigger_refresh()

    def _add_to_group_and_refresh(self, group, wallpaper_id):
        """Add wallpaper to group and refresh gallery display"""
        self.group_manager.add_to_group(group, wallpaper_id)
        self.log(f"[GUI] Added {wallpaper_id} to group '{group}'")
        self._trigger_refresh()

    def _delete_group_and_refresh(self, group_id):
        """Delete group and refresh gallery display"""
        self.group_manager.delete_group(group_id)
        self.log(f"[GUI] Deleted group '{group_id}'")
        self._trigger_refresh()

    def _show_assign_groups_dialog(self, wallpaper_id):
        """Display dialog for assigning wallpaper to groups"""
        self.dialog_manager.show_assign_groups_dialog(
            wallpaper_id,
            on_closed=self.on_refresh_needed
        )