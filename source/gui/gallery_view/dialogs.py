from tkinter import Toplevel, Label, Entry, Button, Frame, Listbox, ttk
from gui.groups import create_group, add_to_group, remove_from_group, in_group
from common.constants import UI_COLORS


class DialogManager:
    """Manages application dialogs for groups and wallpaper assignments"""

    def __init__(self, parent, config, log_callback=None):
        self.parent = parent
        self.config = config
        self.log_callback = log_callback

    def log(self, message: str) -> None:
        """Send message to log if callback is available"""
        if self.log_callback:
            self.log_callback(message)

    def show_new_group_dialog(self, on_created=None):
        """
        Display dialog for creating a new wallpaper group.
        
        on_created: callback function executed after group creation
        """
        win = Toplevel(self.parent)
        win.title("New group")
        win.geometry("250x120")
        win.config(bg=UI_COLORS["bg_secondary"])

        Label(win, text="Group name:", bg=UI_COLORS["bg_secondary"], fg=UI_COLORS["accent_cyan"], font=("Arial", 10, "bold")).pack(pady=5)
        entry = Entry(win, bg=UI_COLORS["text_input_bg"], fg=UI_COLORS["accent_cyan"], insertbackground=UI_COLORS["accent_cyan"], font=("Arial", 10))
        entry.pack(pady=5)
        entry.focus()

        def create():
            name = entry.get().strip()
            if name:
                if create_group(self.config, name):
                    self.log(f"[GUI] Created group: {name}")
                else:
                    self.log(f"[GUI] Group '{name}' already exists")
            win.destroy()
            if on_created:
                on_created()

        def on_enter(event):
            create()

        entry.bind("<Return>", on_enter)
        Button(win, text="CREATE", bg=UI_COLORS["accent_cyan"], fg=UI_COLORS["bg_secondary"], font=("Arial", 10, "bold"), activebackground=UI_COLORS["accent_cyan_bright"], activeforeground=UI_COLORS["bg_secondary"], bd=2, relief="raised", cursor="hand2", command=create).pack(pady=10)

    def show_assign_groups_dialog(self, wallpaper_id, on_closed=None):
        """
        Display dialog for assigning/removing wallpaper from groups.
        
        on_closed: callback function executed when dialog closes
        """
        win = Toplevel(self.parent)
        win.title(f"Assign groups: {wallpaper_id}")
        win.geometry("500x450")

        Label(win, text="Groups").pack(pady=5)


        list_frame = Frame(win)
        list_frame.pack(fill="both", expand=True)

        groups_list = Listbox(list_frame, selectmode="single")
        groups_list.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=groups_list.yview)
        scrollbar.pack(side="right", fill="y")
        groups_list.config(yscrollcommand=scrollbar.set)

        def refresh_list():
            """Refresh the groups list showing which groups are assigned to the wallpaper"""
            groups_list.delete(0, "end")
            for g in self.config["--groups"].keys():
                mark = "✓ " if in_group(self.config, g, wallpaper_id) else "  "
                groups_list.insert("end", f"{mark}{g}")

        refresh_list()

        def get_selected_group():
            """Get the group selected in the list"""
            sel = groups_list.curselection()
            if not sel:
                return None
            text = groups_list.get(sel[0])

            if text.startswith("✓ ") or text.startswith("  "):
                return text[2:].strip()
            return text.strip()

        def add_selected():
            """Add wallpaper to selected group"""
            g = get_selected_group()
            if g:
                add_to_group(self.config, g, wallpaper_id)
                refresh_list()
                self.log(f"[GUI] Added {wallpaper_id} to group '{g}'")

        def remove_selected():
            """Elimina el wallpaper del grupo seleccionado"""
            g = get_selected_group()
            if g:
                remove_from_group(self.config, g, wallpaper_id)
                refresh_list()
                self.log(f"[GUI] Removed {wallpaper_id} from group '{g}'")


        btn_frame = Frame(win)
        btn_frame.pack(pady=5)

        Button(btn_frame, text="Add", command=add_selected).grid(row=0, column=0, padx=5)
        Button(btn_frame, text="Remove", command=remove_selected).grid(row=0, column=1, padx=5)


        Label(win, text="New group:").pack(pady=(10, 0))
        new_entry = Entry(win)
        new_entry.pack(pady=5)

        def create_and_add():
            """Create new group and add wallpaper to it directly"""
            name = new_entry.get().strip()
            if not name:
                return

            if create_group(self.config, name):
                add_to_group(self.config, name, wallpaper_id)
                refresh_list()
                new_entry.delete(0, "end")
                self.log(f"[GUI] Created group '{name}' and added {wallpaper_id}")
            else:
                self.log(f"[GUI] Group '{name}' already exists")

        def on_enter(event):
            create_and_add()

        new_entry.bind("<Return>", on_enter)
        Button(win, text="Create & add", command=create_and_add).pack(pady=5)


        def close():
            if on_closed:
                on_closed()
            win.destroy()

        Button(win, text="Close", command=close).pack(pady=10)


        def on_double_click(event):
            g = get_selected_group()
            if g:
                if in_group(self.config, g, wallpaper_id):
                    remove_selected()
                else:
                    add_selected()

        groups_list.bind("<Double-Button-1>", on_double_click)