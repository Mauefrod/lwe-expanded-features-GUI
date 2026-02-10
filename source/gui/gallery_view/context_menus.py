from tkinter import Menu
from gui.groups import is_favorite, in_group


class ContextMenuManager:
    """Manages context menus for wallpaper and group selections throughout the application"""

    def __init__(self, parent, config):
        self.parent = parent
        self.config = config

    def show_wallpaper_menu(self, event, wallpaper_id, callbacks):
        """
        Display context menu for a wallpaper thumbnail with options for managing it.
        
        callbacks dictionary must contain:
        - on_toggle_favorite: function that receives wallpaper_id
        - on_assign_groups: function that receives wallpaper_id
        - on_add_to_group: function that receives (group, wallpaper_id)
        - on_mark_not_working: function that receives wallpaper_id
        """
        menu = Menu(self.parent, tearoff=0, bg="#1a2f4d", fg="#00d4ff", activebackground="#00d4ff", activeforeground="#0a0e27")


        if is_favorite(self.config, wallpaper_id):
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


        if in_group(self.config, "not working", wallpaper_id):
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


        groups_menu = Menu(menu, tearoff=0, bg="#1a2f4d", fg="#00d4ff", activebackground="#00d4ff", activeforeground="#0a0e27")
        groups = [g for g in self.config["--groups"].keys() if g != "not working"]

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
        menu = Menu(self.parent, tearoff=0, bg="#1a2f4d", fg="#000000", activebackground="#661111", activeforeground="#ffffff")

        if group_id not in ("__ALL__", "__FAVORITES__", "not working"):
            menu.add_command(
                label=f"Delete group '{group_id}'",
                command=lambda: on_delete(group_id)
            )
        else:
            menu.add_command(label="Cannot delete this folder", state="disabled")

        menu.tk_popup(event.x_root, event.y_root)