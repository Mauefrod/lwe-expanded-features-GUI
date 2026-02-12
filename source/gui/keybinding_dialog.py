"""UI component for displaying and managing keybindings"""
"""If like me you have set type checking to strict, you will see a lot of red in this module,
this is just dumbfoolery from the interpreter, you can either: 
1. Ignore it
2. Set your type checking to less strict
3. Ignore it
4. Use type:ignore... not recommended for debbuging
5. Just ignore it"""

from tkinter import Tk, Frame, Label, Button, Listbox, ttk, messagebox, Toplevel, DISABLED, NORMAL
from models.keybindings import KeybindingAction, KeyModifier, Keybinding
from models.config import ConfigManager
from common.constants import UI_COLORS, DEFAULT_WINDOW_HEIGHT
from typing import Callable


class KeybindingEditorDialog:
    """Interactive dialog for binding keys to actions"""

    def __init__(self, parent_window: Tk, keybinding_controller, log_callback: Callable = None):
        """
        Create an interactive keybinding editor dialog.
        
        Args:
            parent_window: Parent window
            keybinding_controller: KeybindingController instance
            log_callback: Optional logging callback
        """
        self.parent_window = parent_window
        self.keybinding_controller = keybinding_controller
        self.log = log_callback or (lambda msg: None)

        self.dialog = None
        self.currently_binding = None
        self.current_modifiers = set()
        self.binding_button = None
        self.status_label = None
        self.bindings_listbox = None


    def show(self):
        """Show the interactive keybinding editor dialog"""

        self.dialog = Toplevel(self.parent_window)
        self.dialog.title("Configure Keybindings")
        self.dialog.geometry(f"700x{DEFAULT_WINDOW_HEIGHT}")
        self.dialog.config(bg=UI_COLORS["bg_primary"])
        self.dialog.resizable(True, True)


        self.dialog.transient(self.parent_window)
        self.dialog.grab_set()


        title = Label(
            self.dialog,
            text="Configure Application Keybindings",
            font=("Arial", 14, "bold"),
            bg=UI_COLORS["bg_primary"],
            fg=UI_COLORS["fg_text"]
        )
        title.pack(pady=10)


        main_frame = Frame(self.dialog, bg=UI_COLORS["bg_primary"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)


        left_frame = Frame(main_frame, bg=UI_COLORS["bg_primary"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        Label(left_frame, text="Click an Action:", bg=UI_COLORS["bg_primary"], fg=UI_COLORS["fg_text"],
              font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))


        action_list_frame = Frame(left_frame, bg=UI_COLORS["bg_secondary"], relief="sunken", borderwidth=1)
        action_list_frame.pack(fill="both", expand=True, pady=(0, 10))

        scrollbar_left = ttk.Scrollbar(action_list_frame)
        scrollbar_left.pack(side="right", fill="y")

        self.action_listbox = Listbox(
            action_list_frame,
            height=15,
            yscrollcommand=scrollbar_left.set
        )
        scrollbar_left.config(command=self.action_listbox.yview)


        self.action_names = [action.value.replace('_', ' ').title() for action in KeybindingAction]
        for action_name in self.action_names:
            self.action_listbox.insert("end", action_name)

        self.action_listbox.pack(fill="both", expand=True, side="left")


        self.action_listbox.bind("<<ListboxSelect>>", self._on_action_selected)


        right_frame = Frame(main_frame, bg=UI_COLORS["bg_primary"])
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        Label(right_frame, text="Bind Key:", bg=UI_COLORS["bg_primary"], fg=UI_COLORS["fg_text"],
              font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))


        self.status_label = Label(
            right_frame,
            text="Select an action and press keys",
            bg=UI_COLORS["bg_secondary"],
            fg=UI_COLORS["accent_orange"],
            font=("Arial", 9),
            wraplength=200,
            justify="left",
            padx=10,
            pady=10
        )
        self.status_label.pack(fill="x", pady=(0, 10))


        self.binding_button = Button(
            right_frame,
            text="Press Key Combination\n(Ctrl, Alt, Shift, then any key)",
            command=self._start_binding,
            bg=UI_COLORS["accent_blue"],
            fg=UI_COLORS["fg_text"],
            height=3,
            font=("Arial", 10)
        )
        self.binding_button.pack(fill="x", pady=(0, 10))


        Label(right_frame, text="Current Bindings:", bg=UI_COLORS["bg_primary"], fg=UI_COLORS["fg_text"],
              font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 5))

        bindings_frame = Frame(right_frame, bg=UI_COLORS["bg_secondary"], relief="sunken", borderwidth=1)
        bindings_frame.pack(fill="both", expand=True, pady=(0, 10))

        scrollbar2 = ttk.Scrollbar(bindings_frame)
        scrollbar2.pack(side="right", fill="y")

        self.bindings_listbox = ttk.Treeview(
            bindings_frame,
            columns=("Key", "Action"),
            height=10,
            yscrollcommand=scrollbar2.set
        )
        scrollbar2.config(command=self.bindings_listbox.yview)

        self.bindings_listbox.column("#0", width=0, stretch=False)
        self.bindings_listbox.column("Key", anchor="w", width=150)
        self.bindings_listbox.column("Action", anchor="w", width=150)

        self.bindings_listbox.heading("#0", text="", anchor="w")
        self.bindings_listbox.heading("Key", text="Key Combo", anchor="w")
        self.bindings_listbox.heading("Action", text="Action", anchor="w")

        self.bindings_listbox.pack(fill="both", expand=True)


        delete_button = Button(
            right_frame,
            text="Delete Selected Binding",
            command=self._delete_binding,
            bg=UI_COLORS["danger_dark"],
            fg=UI_COLORS["fg_text"],
            padx=5
        )
        delete_button.pack(fill="x", pady=(0, 10))


        button_frame = Frame(self.dialog, bg=UI_COLORS["bg_primary"])
        button_frame.pack(pady=10, fill="x", padx=10)

        save_button = Button(
            button_frame,
            text="Save & Close",
            command=self._on_save,
            bg=UI_COLORS["accent_blue"],
            fg=UI_COLORS["fg_text"],
            padx=15
        )
        save_button.pack(side="left", padx=5)

        close_button = Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            bg=UI_COLORS["button_cancel"],
            fg=UI_COLORS["fg_text"],
            padx=15
        )
        close_button.pack(side="left", padx=5)


        self._refresh_bindings_display()


        self.dialog.bind("<KeyPress>", self._on_dialog_key_press)
        self.dialog.bind("<KeyRelease>", self._on_dialog_key_release)

    def _on_action_selected(self, event):
        """Handle action selection from the listbox"""
        selection = self.action_listbox.curselection()
        if not selection:
            return


        index = selection[0]
        self.currently_binding = self.action_names[index]


        self.status_label.config(
            text=f"Selected: {self.currently_binding}\n\nClick 'Press Key Combination'\nto bind this action",
            fg=UI_COLORS["accent_orange"]
        )


        self.binding_button.config(state=NORMAL, bg=UI_COLORS["accent_orange_bright"])

    def _start_binding(self):
        """Start capturing key presses for binding"""
        if not self.currently_binding:
            messagebox.showwarning("Select Action", "Please select an action first")
            return
        self.current_modifiers = set()

        self.binding_button.config(state=DISABLED, bg=UI_COLORS["button_disabled"])
        self.status_label.config(
            text=f"Binding: {self.currently_binding}\n\nPress Ctrl, Alt, Shift\n(hold them), then press any key",
            fg=UI_COLORS["accent_green_success"]
        )
        self.binding_button.focus_set()

    def _on_dialog_key_press(self, event):
        """Handle key press events"""
        if not self.currently_binding:
            return


        if event.keysym in ("Control_L", "Control_R"):
            self.current_modifiers.add("ctrl")
        elif event.keysym in ("Alt_L", "Alt_R"):
            self.current_modifiers.add("alt")
        elif event.keysym in ("Shift_L", "Shift_R"):
            self.current_modifiers.add("shift")
        elif event.keysym == "Super_L":
            self.current_modifiers.add("super")

    def _on_dialog_key_release(self, event):
        """Handle key release events - this is where we capture the binding"""
        if not self.currently_binding:
            return


        if event.keysym not in ("Control_L", "Control_R", "Alt_L", "Alt_R",
                                "Shift_L", "Shift_R", "Super_L"):
            key = event.keysym
            modifiers = list(self.current_modifiers)


            action_display = self.currently_binding
            action_value = action_display.lower().replace(' ', '_')

            try:
                action = KeybindingAction(action_value)


                keybinding = Keybinding(
                    key=key,
                    action=action,
                    modifiers=[KeyModifier(m) for m in modifiers],
                    enabled=True,
                    description=action_display
                )


                if self.keybinding_controller.keybinding_service.keybinding_manager.add_binding(keybinding):
                    self.log(f"[KEYBIND] Bound {action_display} to {keybinding.get_keybind_string()}")
                    messagebox.showinfo("Success", f"Bound {action_display} to {keybinding.get_keybind_string()}")
                    self._refresh_bindings_display()
                else:
                    self.log(f"[KEYBIND] Failed to bind - duplicate keybinding detected")
                    messagebox.showwarning("Duplicate", "This key combination is already bound to another action")
            except Exception as e:
                self.log(f"[KEYBIND ERROR] {str(e)}")
                messagebox.showerror("Error", f"Failed to bind key: {str(e)}")


            self.currently_binding = None
            self.current_modifiers = set()
            self.binding_button.config(state=NORMAL, bg=UI_COLORS["accent_blue"])
            self.status_label.config(text="Select an action and press keys", fg=UI_COLORS["accent_orange"])

    def _refresh_bindings_display(self):
        """Refresh the display of current bindings"""

        for item in self.bindings_listbox.get_children():
            self.bindings_listbox.delete(item)


        for binding in self.keybinding_controller.keybinding_service.keybinding_manager.get_all_bindings():
            keybind_str = binding.get_keybind_string()
            action_display = binding.action.value.replace('_', ' ').title()
            self.bindings_listbox.insert("", "end", values=(keybind_str, action_display))

    def _delete_binding(self):
        """Delete the selected binding"""
        selected = self.bindings_listbox.selection()
        if not selected:
            messagebox.showinfo("Select Binding", "Please select a binding to delete")
            return

        item = selected[0]
        values = self.bindings_listbox.item(item, "values")
        keybind_str = values[0]

        if messagebox.askyesno("Confirm Delete", f"Delete binding: {keybind_str}?"):

            parts = keybind_str.split("+")
            key = parts[-1].lower() if parts[-1].lower() != "enter" else parts[-1]
            modifiers = [KeyModifier(p.lower()) for p in parts[:-1]]

            if self.keybinding_controller.keybinding_service.keybinding_manager.remove_binding(key, modifiers):
                self.log(f"[KEYBIND] Removed binding: {keybind_str}")
                self._refresh_bindings_display()
                messagebox.showinfo("Success", "Binding deleted")
            else:
                messagebox.showerror("Error", "Failed to delete binding")

    def _on_save(self):
        """Save keybindings and close"""
        try:
            self.keybinding_controller.keybinding_service.save_keybindings()
            ConfigManager.save(self.keybinding_controller.config)
            self.log("[KEYBIND] Keybindings saved to configuration")
            messagebox.showinfo("Success", "Keybindings saved successfully")
            self.dialog.destroy()
        except Exception as e:
            self.log(f"[KEYBIND ERROR] Failed to save keybindings: {str(e)}")
            messagebox.showerror("Error", f"Failed to save keybindings: {str(e)}")
