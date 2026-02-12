from tkinter import Frame, Entry, Button, Label, BooleanVar, Checkbutton, Text, Canvas, ttk
from common.constants import UI_COLORS, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT


class LogArea:
    """Manages the application log display area with colored text output"""

    def __init__(self, parent):
        self.frame = Frame(parent, bg=UI_COLORS["bg_secondary"], bd=2, relief="solid", highlightthickness=2, highlightcolor=UI_COLORS["accent_blue"], highlightbackground=UI_COLORS["accent_blue"])

        self.text_widget = Text(
            self.frame,
            height=12,
            bg=UI_COLORS["bg_tertiary"],
            fg=UI_COLORS["accent_green_success"],
            insertbackground=UI_COLORS["accent_cyan"],
            wrap="word",
            bd=0,
            font=("Courier", 9)
        )
        self.text_widget.pack(fill="both", expand=True, padx=2, pady=2)

    def log(self, message):
        """Add a message to the log display"""
        try:
            self.text_widget.insert("end", message + "\n")
            self.text_widget.see("end")
            self.text_widget.update_idletasks()
        except Exception as e:
            print(f"[LOG_ERROR] Error writing to log: {str(e)}")

    def clear(self):
        """Limpia el log"""
        self.text_widget.delete("1.0", "end")

    def grid(self, **kwargs):
        """Posiciona el frame en la ventana"""
        self.frame.grid(**kwargs)

    def grid_remove(self):
        """Oculta el frame sin quitarlo del layout"""
        self.frame.grid_remove()

    def grid_show(self):
        """Muestra el frame nuevamente"""
        self.frame.grid()


class DirectoryControls:
    """Manages directory selection controls and directory display"""

    def __init__(self, parent):
        self.frame = Frame(parent)


        Label(self.frame, text="DIR ").grid(column=0, row=0)


        self.entry = Entry(self.frame, state="readonly")
        self.entry.grid(column=1, row=0)


        self.pick_button = Button(self.frame, text="PICK DIR")
        self.pick_button.grid(column=1, row=1)

        self.explore_button = Button(self.frame, text="EXPLORE")
        self.explore_button.grid(column=0, row=1)

        self.execute_button = Button(self.frame, text="EXECUTE")
        self.execute_button.grid(column=0, row=2)

        self.stop_button = Button(self.frame, text="STOP")
        self.stop_button.grid(column=0, row=6, pady=5)

    def set_directory(self, path):
        """Update displayed directory path"""
        self.entry.config(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, path)
        self.entry.config(state="readonly")

    def grid(self, **kwargs):
        """Posiciona el frame en la ventana"""
        self.frame.grid(**kwargs)


class FlagsPanel:
    """Manages wallpaper engine flags and configuration options panel"""

    def __init__(self, parent):
        self.frame = Frame(parent)


        self.window_mode = BooleanVar()
        self.above_flag = BooleanVar()
        self.random_mode = BooleanVar()


        self.window_checkbox = Checkbutton(
            self.frame,
            text="window mode",
            variable=self.window_mode
        )
        self.window_checkbox.grid(column=0, row=0)

        self.above_checkbox = Checkbutton(
            self.frame,
            text="remove above prio",
            variable=self.above_flag
        )
        self.above_checkbox.grid(column=0, row=1)

        self.random_checkbox = Checkbutton(
            self.frame,
            text="random mode",
            variable=self.random_mode
        )
        self.random_checkbox.grid(column=0, row=2)


        self.back_button = Button(self.frame, text="<= BACK")
        self.back_button.grid(column=0, row=3, pady=(10, 0))


        self.clear_log_button = Button(self.frame, text="CLEAR LOG")
        self.clear_log_button.grid(column=0, row=4, pady=5)


        self.dynamic_widgets = []

    def add_timer_controls(self, on_submit):
        """Add timer control widgets for random wallpaper mode"""
        self.clear_dynamic_widgets()

        label = Label(self.frame, text="TIMER (s)")
        entry = Entry(self.frame, width=5, justify="center")
        submit_button = Button(self.frame, text="SUBMIT")

        label.grid(column=1, row=0)
        entry.grid(column=1, row=1)
        submit_button.grid(column=1, row=2)

        self.dynamic_widgets.extend([label, entry, submit_button])


        submit_button.config(command=lambda: on_submit(entry.get()))

        return entry

    def clear_dynamic_widgets(self):
        """Remove all dynamically created widget controls"""
        for widget in self.dynamic_widgets:
            widget.destroy()
        self.dynamic_widgets.clear()

    def grid(self, **kwargs):
        """Position the frame in the window"""
        self.frame.grid(**kwargs)


class GalleryCanvas:
    """Manages gallery display canvas with scrollbar for content navigation"""

    def __init__(self, parent):
        self.container = Frame(parent)


        self.canvas = Canvas(self.container, width=DEFAULT_WINDOW_WIDTH, height=DEFAULT_WINDOW_HEIGHT, bg=UI_COLORS["bg_canvas"])
        self.canvas.pack(side="left", fill="both", expand=True)


        self.scrollbar = ttk.Scrollbar(
            self.container,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)


        self.inner_frame = Frame(self.canvas, bg=UI_COLORS["bg_canvas"])
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

    def update_scroll_region(self, event=None):
        """Update canvas scroll region to match content size"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def bind_scroll_events(self, on_mousewheel):
        """Configure mouse wheel scroll event handlers"""
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.canvas.bind_all("<Button-4>", on_mousewheel)
        self.canvas.bind_all("<Button-5>", on_mousewheel)

    def grid(self, **kwargs):
        """Position the container in the window"""
        self.container.grid(**kwargs)