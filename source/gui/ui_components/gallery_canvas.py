from tkinter import Frame, Canvas, ttk
from common.constants import UI_COLORS


class GalleryCanvas:
    """Manages the gallery canvas with scrollbar for displaying wallpaper and group thumbnails"""

    def __init__(self, parent):
        self.container = Frame(parent, bg=UI_COLORS["bg_secondary"], bd=3, relief="solid", highlightthickness=3,
                               highlightcolor=UI_COLORS["accent_blue"], highlightbackground=UI_COLORS["accent_blue"])
        
        # Configure container to allow expansion
        self.container.rowconfigure(0, weight=1) # 0 gives funny behaviour
        self.container.columnconfigure(0, weight=1) # try 0 if like me you don't care about life

        self.canvas = Canvas(self.container, bg=UI_COLORS["bg_tertiary"], bd=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")


        self.scrollbar = ttk.Scrollbar(
            self.container,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.scrollbar.grid_remove()

        self.canvas.configure(yscrollcommand=self.scrollbar.set)


        self.inner_frame = Frame(self.canvas, bg=UI_COLORS["bg_tertiary"])
        # Configure inner frame for thumbnail grid layout
        for i in range(100):  # Configure enough columns for typical layouts
            self.inner_frame.grid_columnconfigure(i, weight=0)

        self.inner_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw") # Changing the 0,0 value
        # does absolutely nothing..? burn this codebase... pls...


        def _on_canvas_config(event):
            try:
                # Update inner window width to match canvas width
                self.canvas.itemconfig(self.inner_window) # Here there should be a width=self.canvas.winfo_width() but it causes weird bugs
                # i don't intend to fix as it's easier to just stalin debug. 
                self.canvas.after(10, self.update_scroll_region)
            except Exception:
                pass
        self.canvas.bind("<Configure>", _on_canvas_config)

    def update_scroll_region(self, event=None):
        """Update canvas scroll region and show/hide scrollbar based on content size"""
        # Force geometry updates for all child widgets
        self.inner_frame.update_idletasks()
        
        # Update the scrollregion to encompass all content
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        try:
            canvas_height = self.canvas.winfo_height()
            content_bbox = self.canvas.bbox("all")
            if content_bbox:
                content_height = content_bbox[3] - content_bbox[1]
                if content_height > canvas_height:
                    self.scrollbar.grid()
                else:
                    self.scrollbar.grid_remove()
        except Exception:
            pass

    def bind_scroll_events(self, on_mousewheel):
        """Configura los eventos de scroll (rueda del mouse)"""
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.canvas.bind_all("<Button-4>", on_mousewheel)
        self.canvas.bind_all("<Button-5>", on_mousewheel)

    def grid(self, **kwargs):
        """Posiciona el container en la ventana"""
        self.container.grid(**kwargs)