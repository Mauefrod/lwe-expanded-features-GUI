from tkinter import Frame, Entry, Button, Label, BooleanVar, Checkbutton
from common.constants import UI_COLORS


class FlagsPanel:
    """Manages flags and options panel for engine configuration"""

    def __init__(self, parent):
        self.frame = Frame(parent, bg=UI_COLORS["bg_secondary"], bd=2, relief="solid",
                           highlightthickness=2, highlightcolor=UI_COLORS["accent_blue"], 
                           highlightbackground=UI_COLORS["accent_blue"])


        self.window_mode = BooleanVar()
        self.above_flag = BooleanVar()
        self.random_mode = BooleanVar()
        self.logs_visible = BooleanVar(value=True) # logs visible by default
        self.startup = BooleanVar()


        self.window_checkbox = Checkbutton(
            self.frame,
            text="window mode",
            variable=self.window_mode,
            bg=UI_COLORS["bg_secondary"],
            fg=UI_COLORS["fg_text"],
            font=("Arial", 9, "bold"),
            activebackground=UI_COLORS["bg_secondary"],
            activeforeground=UI_COLORS["accent_red"],
            selectcolor=UI_COLORS["bg_secondary"]
        )
        self.window_checkbox.grid(column=0, row=0, padx=5, pady=5, sticky="w")

        self.startup_checkbox = Checkbutton(
            self.frame, text="run at startup",
            variable=self.startup,
            bg=UI_COLORS["bg_secondary"],
            fg=UI_COLORS["fg_text"],
            font=("Arial", 9, "bold"),
            activebackground=UI_COLORS["bg_secondary"],
            activeforeground=UI_COLORS["accent_red"],
            selectcolor=UI_COLORS["bg_secondary"]
        )
        self.startup_checkbox.grid(column=0, row=1, padx=5, pady=5, sticky="w")

        self.above_checkbox = Checkbutton(
            self.frame,
            text="remove above prio",
            variable=self.above_flag,
            bg=UI_COLORS["bg_secondary"],
            fg=UI_COLORS["fg_text"],
            font=("Arial", 9, "bold"),
            activebackground=UI_COLORS["bg_secondary"],
            activeforeground=UI_COLORS["accent_red"],
            selectcolor=UI_COLORS["bg_secondary"]
        )
        self.above_checkbox.grid(column=0, row=2, padx=5, pady=5, sticky="w")

        self.random_checkbox = Checkbutton(
            self.frame,
            text="random mode",
            variable=self.random_mode,
            bg=UI_COLORS["bg_secondary"],
            fg=UI_COLORS["fg_text"],
            font=("Arial", 9, "bold"),
            activebackground=UI_COLORS["bg_secondary"],
            activeforeground=UI_COLORS["accent_red"],
            selectcolor=UI_COLORS["bg_secondary"]
        )
        self.random_checkbox.grid(column=0, row=3, padx=5, pady=5, sticky="w")

        self.logs_checkbox = Checkbutton(
            self.frame,
            text="show logs",
            variable=self.logs_visible,
            bg=UI_COLORS["bg_secondary"],
            fg=UI_COLORS["fg_text"],
            font=("Arial", 9, "bold"),
            activebackground=UI_COLORS["bg_secondary"],
            activeforeground=UI_COLORS["accent_red"],
            selectcolor=UI_COLORS["bg_secondary"]
        )
        self.logs_checkbox.grid(column=0, row=4, padx=5, pady=5, sticky="w")


        self.back_button = Button(self.frame, text="BACK", bg=UI_COLORS["accent_blue"], fg=UI_COLORS["fg_text"], font=("Arial", 9, "bold"), activebackground=UI_COLORS["accent_blue_light"], activeforeground=UI_COLORS["accent_red"], bd=2, relief="raised", cursor="hand2")
        self.back_button.grid(column=0, row=5, padx=5, pady=(10, 5))


        self.clear_log_button = Button(self.frame, text="CLEAR LOG", bg=UI_COLORS["danger_dark"], fg=UI_COLORS["fg_text"], font=("Arial", 9, "bold"), activebackground=UI_COLORS["danger_light"], activeforeground=UI_COLORS["accent_red"], bd=2, relief="raised", cursor="hand2")
        self.clear_log_button.grid(column=0, row=6, padx=5, pady=5)


        self.keybindings_button = Button(self.frame, text="KEYBINDINGS", bg=UI_COLORS["accent_green"], fg=UI_COLORS["fg_text"], font=("Arial", 9, "bold"), activebackground=UI_COLORS["accent_green_light"], activeforeground=UI_COLORS["accent_red"], bd=2, relief="raised", cursor="hand2")
        self.keybindings_button.grid(column=0, row=7, padx=5, pady=5)


        self.dynamic_widgets = []

    def add_timer_controls(self, on_submit):
        """Add timer control widgets for random wallpaper mode"""
        self.clear_dynamic_widgets()

        label = Label(self.frame, text="TIMER (s)", bg=UI_COLORS["bg_secondary"], fg=UI_COLORS["fg_text"], font=("Arial", 9, "bold"))
        entry = Entry(self.frame, width=5, justify="center", bg=UI_COLORS["text_input_bg"], fg=UI_COLORS["fg_text"], insertbackground=UI_COLORS["text_input_cursor"], font=("Courier", 10, "bold"))
        submit_button = Button(self.frame, text="SUBMIT", bg=UI_COLORS["accent_blue"], fg=UI_COLORS["fg_text"], font=("Arial", 9, "bold"), activebackground=UI_COLORS["accent_blue_light"], activeforeground=UI_COLORS["accent_red"], bd=2, relief="raised", cursor="hand2")

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
        """Posiciona el frame en la ventana"""
        self.frame.grid(**kwargs)