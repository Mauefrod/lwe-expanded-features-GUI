from tkinter import Menu
from models.groups import GroupManager
from common.constants import UI_COLORS


class ContextMenuManager:
    """Manages context menus for wallpaper and group selections throughout the application"""

    def __init__(self, parent, config, group_manager=None):
        self.parent = parent
        self.config = config
        # Use injected group manager or create one
        self.group_manager = group_manager or GroupManager(config)

    def show_wallpaper_menu(self, event, wallpaper_id, callbacks):
        """
        Display context menu for a wallpaper thumbnail with options for managing it.
        
        callbacks dictionary must contain:
        - on_toggle_favorite: function that receives wallpaper_id
        - on_assign_groups: function that receives wallpaper_id
        - on_add_to_group: function that receives (group, wallpaper_id)
        - on_mark_not_working: function that receives wallpaper_id
        """
        menu = Menu(self.parent, tearoff=0, bg=UI_COLORS["text_input_bg"], fg=UI_COLORS["accent_cyan"], activebackground=UI_COLORS["accent_cyan"], activeforeground=UI_COLORS["bg_secondary"])


        if self.group_manager.is_favorite(wallpaper_id):
            menu.add_command(
                label="Remove from favorites",
                command=lambda: callbacks['on_toggle_favorite'](wallpaper_id)
            )
        else:
            menu.add_command(
                label="Add to favorites",
                command=lambda: callbacks['on_toggle_favorite'](wallpaper_id)
            )

        menu.add_separator()


        if self.group_manager.in_group("not working", wallpaper_id):
            menu.add_command(
                label="Remove from not working",
                command=lambda: callbacks['on_mark_not_working'](wallpaper_id)
            )
        else:
            menu.add_command(
                label="Mark as not working",
                command=lambda: callbacks['on_mark_not_working'](wallpaper_id)
            )

        menu.add_separator()


        menu.add_command(
            label="Assign to group",
            command=lambda: callbacks['on_assign_groups'](wallpaper_id)
        )


        groups_menu = Menu(menu, tearoff=0, bg=UI_COLORS["text_input_bg"], fg=UI_COLORS["accent_cyan"], activebackground=UI_COLORS["accent_cyan"], activeforeground=UI_COLORS["bg_secondary"])
        groups = [g for g in self.group_manager.get_all_groups() if g != "not working"]

        if groups:
            for g in groups:
                groups_menu.add_command(
                    label=g,
                    command=lambda group=g: callbacks['on_add_to_group'](group, wallpaper_id)
                )
        else:
            groups_menu.add_command(label="No groups", state="disabled")

        menu.add_cascade(label="Add to group", menu=groups_menu)

        menu.tk_popup(event.x_root, event.y_root)

    def show_group_menu(self, event, group_id, on_delete):
        """
        Display context menu for a group with management options.
        
        on_delete: function that receives group_id
        """
        menu = Menu(self.parent, tearoff=0, bg=UI_COLORS["text_input_bg"], fg=UI_COLORS["fg_text_dark"], activebackground=UI_COLORS["danger_dark"], activeforeground=UI_COLORS["fg_text"])

        if group_id not in ("__ALL__", "__FAVORITES__", "not working"):
            menu.add_command(
                label=f"Delete group '{group_id}'",
                command=lambda: on_delete(group_id)
            )
        else:
            menu.add_command(label="Cannot delete this folder", state="disabled")

        menu.tk_popup(event.x_root, event.y_root)