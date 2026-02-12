from tkinter import Frame, Label, BooleanVar, Checkbutton
from common.constants import UI_COLORS


class SoundPanel:
    """Manages audio configuration options"""

    def __init__(self, parent):
        self.frame = Frame(
            parent,
            bg=UI_COLORS["bg_secondary"],
            bd=2,
            relief="solid",
            highlightthickness=2,
            highlightcolor=UI_COLORS["accent_purple"],
            highlightbackground=UI_COLORS["accent_purple"]
        )


        title_label = Label(
            self.frame,
            text="🔊 SOUND",
            bg=UI_COLORS["bg_secondary"],
            fg=UI_COLORS["fg_text"],
            font=("Arial", 10, "bold")
        )
        title_label.grid(column=0, row=0, columnspan=2, pady=(5, 10), sticky="w", padx=5)


        self.silent = BooleanVar()
        self.noautomute = BooleanVar()
        self.no_audio_processing = BooleanVar()


        self.silent_checkbox = Checkbutton(
            self.frame,
            text="Silent (mute all)",
            variable=self.silent,
            bg=UI_COLORS["bg_secondary"],
            fg=UI_COLORS["fg_text"],
            font=("Arial", 9),
            activebackground=UI_COLORS["bg_secondary"],
            activeforeground=UI_COLORS["accent_red"],
            selectcolor=UI_COLORS["bg_secondary"]
        )
        self.silent_checkbox.grid(column=0, row=1, columnspan=2, padx=5, pady=3, sticky="w")


        self.noautomute_checkbox = Checkbutton(
            self.frame,
            text="No auto mute",
            variable=self.noautomute,
            bg=UI_COLORS["bg_secondary"],
            fg=UI_COLORS["fg_text"],
            font=("Arial", 9),
            activebackground=UI_COLORS["bg_secondary"],
            activeforeground=UI_COLORS["accent_red"],
            selectcolor=UI_COLORS["bg_secondary"]
        )
        self.noautomute_checkbox.grid(column=0, row=2, columnspan=2, padx=5, pady=3, sticky="w")


        self.no_audio_processing_checkbox = Checkbutton(
            self.frame,
            text="No audio processing",
            variable=self.no_audio_processing,
            bg=UI_COLORS["bg_secondary"],
            fg=UI_COLORS["fg_text"],
            font=("Arial", 9),
            activebackground=UI_COLORS["bg_secondary"],
            activeforeground=UI_COLORS["accent_red"],
            selectcolor=UI_COLORS["bg_secondary"]
        )
        self.no_audio_processing_checkbox.grid(column=0, row=3, columnspan=2, padx=5, pady=(3, 10), sticky="w")

    def grid(self, **kwargs) -> None:
        """Position the frame in the parent window"""
        self.frame.grid(**kwargs)