from tkinter import Frame, Entry, Button, Label
from common.constants import UI_COLORS


class DirectoryControls:
    """Manages directory selection and display controls"""

    def __init__(self, parent):
        self.frame = Frame(parent, bg=UI_COLORS["bg_secondary"], bd=2, relief="solid", highlightthickness=2, highlightcolor=UI_COLORS["accent_blue"], highlightbackground=UI_COLORS["accent_blue"])


        Label(self.frame, text="DIR ", bg=UI_COLORS["bg_secondary"], fg=UI_COLORS["fg_text"], font=("Arial", 10, "bold")).grid(column=0, row=0, padx=5, pady=5)


        self.entry = Entry(self.frame, state="readonly", bg=UI_COLORS["text_input_bg"], fg=UI_COLORS["fg_text_dark"], insertbackground=UI_COLORS["text_input_cursor"], font=("Courier", 9))
        self.entry.grid(column=1, row=0, padx=5, pady=5)


        self.pick_button = Button(self.frame, text="PICK DIR", bg=UI_COLORS["accent_blue"], fg=UI_COLORS["fg_text"], font=("Arial", 9, "bold"), activebackground=UI_COLORS["accent_blue_light"], activeforeground=UI_COLORS["accent_red"], bd=2, relief="raised", cursor="hand2")
        self.pick_button.grid(column=1, row=1, padx=5, pady=5)

        self.explore_button = Button(self.frame, text="EXPLORE", bg=UI_COLORS["accent_blue"], fg=UI_COLORS["fg_text"], font=("Arial", 9, "bold"), activebackground=UI_COLORS["accent_blue_light"], activeforeground=UI_COLORS["accent_red"], bd=2, relief="raised", cursor="hand2")
        self.explore_button.grid(column=0, row=1, padx=5, pady=5)

        self.execute_button = Button(self.frame, text="EXECUTE", bg=UI_COLORS["accent_blue"], fg=UI_COLORS["fg_text"], font=("Arial", 9, "bold"), activebackground=UI_COLORS["accent_blue_light"], activeforeground=UI_COLORS["accent_red"], bd=2, relief="raised", cursor="hand2")
        self.execute_button.grid(column=0, row=2, padx=5, pady=5)

        self.stop_button = Button(self.frame, text="STOP", bg=UI_COLORS["danger_dark"], fg=UI_COLORS["fg_text"], font=("Arial", 9, "bold"), activebackground=UI_COLORS["danger_light"], activeforeground=UI_COLORS["accent_red"], bd=2, relief="raised", cursor="hand2")
        self.stop_button.grid(column=0, row=6, padx=5, pady=10)

    def set_directory(self, path: str) -> None:
        """Update displayed directory path"""
        self.entry.config(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, path)
        self.entry.config(state="readonly")

    def grid(self, **kwargs) -> None:
        """Position the frame in the parent window"""
        self.frame.grid(**kwargs)