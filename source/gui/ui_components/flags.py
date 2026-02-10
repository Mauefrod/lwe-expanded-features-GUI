from tkinter import Frame, Entry, Button, Label, BooleanVar, Checkbutton


class FlagsPanel:
    """Manages flags and options panel for engine configuration"""

    def __init__(self, parent):
        self.frame = Frame(parent, bg="#0a0e27", bd=2, relief="solid",
                           highlightthickness=2, highlightcolor="#004466", highlightbackground="#004466")


        self.window_mode = BooleanVar()
        self.above_flag = BooleanVar()
        self.random_mode = BooleanVar()
        self.logs_visible = BooleanVar(value=True)
        self.startup = BooleanVar()


        self.window_checkbox = Checkbutton(
            self.frame,
            text="window mode",
            variable=self.window_mode,
            bg="#0a0e27",
            fg="#FFFFFF",
            font=("Arial", 9, "bold"),
            activebackground="#0a0e27",
            activeforeground="#ff3333",
            selectcolor="#0a0e27"
        )
        self.window_checkbox.grid(column=0, row=0, padx=5, pady=5, sticky="w")

        self.startup_checkbox = Checkbutton(
            self.frame, text="run at startup",
            variable=self.startup,
            bg="#0a0e27",
            fg="#FFFFFF",
            font=("Arial", 9, "bold"),
            activebackground="#0a0e27",
            activeforeground="#ff3333",
            selectcolor="#0a0e27"
        )
        self.startup_checkbox.grid(column=0, row=1, padx=5, pady=5, sticky="w")

        self.above_checkbox = Checkbutton(
            self.frame,
            text="remove above prio",
            variable=self.above_flag,
            bg="#0a0e27",
            fg="#FFFFFF",
            font=("Arial", 9, "bold"),
            activebackground="#0a0e27",
            activeforeground="#ff3333",
            selectcolor="#0a0e27"
        )
        self.above_checkbox.grid(column=0, row=2, padx=5, pady=5, sticky="w")

        self.random_checkbox = Checkbutton(
            self.frame,
            text="random mode",
            variable=self.random_mode,
            bg="#0a0e27",
            fg="#FFFFFF",
            font=("Arial", 9, "bold"),
            activebackground="#0a0e27",
            activeforeground="#ff3333",
            selectcolor="#0a0e27"
        )
        self.random_checkbox.grid(column=0, row=3, padx=5, pady=5, sticky="w")

        self.logs_checkbox = Checkbutton(
            self.frame,
            text="show logs",
            variable=self.logs_visible,
            bg="#0a0e27",
            fg="#FFFFFF",
            font=("Arial", 9, "bold"),
            activebackground="#0a0e27",
            activeforeground="#ff3333",
            selectcolor="#0a0e27"
        )
        self.logs_checkbox.grid(column=0, row=4, padx=5, pady=5, sticky="w")


        self.back_button = Button(self.frame, text="BACK", bg="#004466", fg="#FFFFFF", font=("Arial", 9, "bold"), activebackground="#0066aa", activeforeground="#ff3333", bd=2, relief="raised", cursor="hand2")
        self.back_button.grid(column=0, row=5, padx=5, pady=(10, 5))


        self.clear_log_button = Button(self.frame, text="CLEAR LOG", bg="#661111", fg="#ffffff", font=("Arial", 9, "bold"), activebackground="#881111", activeforeground="#ff3333", bd=2, relief="raised", cursor="hand2")
        self.clear_log_button.grid(column=0, row=6, padx=5, pady=5)


        self.keybindings_button = Button(self.frame, text="KEYBINDINGS", bg="#00AA44", fg="#ffffff", font=("Arial", 9, "bold"), activebackground="#00CC55", activeforeground="#ff3333", bd=2, relief="raised", cursor="hand2")
        self.keybindings_button.grid(column=0, row=7, padx=5, pady=5)


        self.dynamic_widgets = []

    def add_timer_controls(self, on_submit):
        """Add timer control widgets for random wallpaper mode"""
        self.clear_dynamic_widgets()

        label = Label(self.frame, text="TIMER (s)", bg="#0a0e27", fg="#FFFFFF", font=("Arial", 9, "bold"))
        entry = Entry(self.frame, width=5, justify="center", bg="#1a2f4d", fg="#FFFFFF", insertbackground="#004466", font=("Courier", 10, "bold"))
        submit_button = Button(self.frame, text="SUBMIT", bg="#004466", fg="#FFFFFF", font=("Arial", 9, "bold"), activebackground="#0066aa", activeforeground="#ff3333", bd=2, relief="raised", cursor="hand2")

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