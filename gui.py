import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from PIL import Image, ImageTk, ImageSequence
import file_handling  # Đảm bảo import file_handling ở đầu file
import config  # Import config for constants
import sys  # For sys.platform
import threading


class ScrolledFrame(tk.Frame):
    """A scrollable frame using a canvas and scrollbars."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Create canvas and scrollbars.  Make canvas background dark gray.
        self.canvas = tk.Canvas(self, bg=config.FRAME_COLOR, highlightthickness=0, bd=0)  # Use config.FRAME_COLOR
        self.scrollbar_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                        troughcolor=config.FRAME_COLOR, bg=config.BUTTON_COLOR, activebackground=config.BUTTON_ACTIVE_COLOR,
                                        width=12)  # Thicker, styled scrollbar
        # No horizontal scrollbar needed
        # self.scrollbar_x = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)  # xscrollcommand removed

        # Pack the scrollbar and canvas
        self.scrollbar_y.pack(side="right", fill="y")
        # self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create the inner frame inside the canvas
        self.inner_frame = tk.Frame(self.canvas, bg=config.FRAME_COLOR)  # Use config.FRAME_COLOR
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Bind events for scrolling and resizing
        self.inner_frame.bind("<Configure>", self._configure_inner_frame)
        self.canvas.bind("<Configure>", self._configure_canvas)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Bind mousewheel to the canvas
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)

    def _configure_inner_frame(self, event):
        # Update the scroll region to match the size of the inner frame
        size = (self.inner_frame.winfo_reqwidth(), self.inner_frame.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.inner_frame.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the canvas's width to fit the inner frame
            self.canvas.config(width=self.inner_frame.winfo_reqwidth())

    def _configure_canvas(self, event):
        if self.inner_frame.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.canvas_frame, width=self.canvas.winfo_width())

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")


# --- Global Variables ---
root = None
file_frame = None
file_label = None
status_bar = None
btn_translate = None
btn_apply_color = None
btn_pause = None
btn_open_folder = None
color_label = None
preview_label = None
format_dropdown = None
color_button = None
selected_format = None  # Use StringVar in main.py
selected_color = None  # Use StringVar in main.py


def choose_color(selected_color, preview_label, format_dropdown):
    """Opens a color chooser and updates the selected color."""
    color_code = colorchooser.askcolor(title="Chọn màu chữ")
    if color_code[1]:
        selected_color.set(color_code[1])  # Update the StringVar
        color_label.config(text=f"Màu chữ: {selected_color.get()}")
        update_preview(selected_color, format_dropdown, preview_label)  # Update preview


def toggle_pause(paused, pause_event, btn_pause):
    """Toggles the pause state."""
    paused = not paused
    if paused:
        btn_pause.config(text="▶ Tiếp tục")
        pause_event.clear()  # Clear the event to pause
    else:
        btn_pause.config(text="⏸ Tạm dừng")
        pause_event.set()  # Set the event to resume
    return paused  # Corrected indentation


def show_about():
    messagebox.showinfo("About", f"{config.APP_NAME} v{config.APP_VERSION}\n{config.COPYRIGHT_NOTICE}\nDeveloped by: NhemNhem")


def update_preview(selected_color, format_dropdown, preview_label):
    """Updates the preview label with the selected color and format."""
    color = selected_color.get()
    current_format = format_dropdown.get()

    if current_format == ".srt":
        preview_text = config.PREVIEW_TEXT_SRT.replace("{color}", color)
    elif current_format == ".ass":
        preview_text = config.PREVIEW_TEXT_ASS.replace("{color}", color[1:])  # Bỏ dấu #
    else:
        preview_text = ""

    preview_label.config(text=preview_text, foreground=color)


# Dictionaries to store references to file-specific widgets
file_status = {}
file_widgets = {}


# Wrapper functions
def start_translation_wrapper():
    """Wrapper function to call start_translation from file_handling."""
    file_handling.start_translation(
        file_paths,
        gui.file_frame,
        gui.file_status,
        gui.file_widgets,
        gui.selected_format,
        gui.selected_color,
        gui.root,
        stop_translation,
        paused,
        pause_event,
        translated_files
    )


def on_format_change(*args):
    """Callback when the format dropdown changes."""
    gui.update_preview(gui.selected_color, gui.format_dropdown, gui.preview_label)


def cancel_translation_wrapper():
    global stop_translation
    stop_translation = True
    file_handling.cancel_translation(stop_translation)


def toggle_pause_wrapper():
    global paused
    paused = gui.toggle_pause(paused, file_handling.pause_event, gui.btn_pause)


def clear_files():
    """Clears the selected files and resets the UI."""
    global file_paths, translated_files  # Good to list globals being modified
    file_paths = []
    translated_files = []

    for widget in gui.file_frame.inner_frame.winfo_children():  # Corrected frame to clear widgets from inner_frame
        widget.destroy()

    gui.file_status.clear()
    gui.file_widgets.clear()

    gui.file_label.config(text="Chưa chọn file", foreground=config.LABEL_COLOR)
    gui.btn_translate.config(state=tk.DISABLED)
    gui.btn_apply_color.config(state=tk.DISABLED)
    gui.btn_open_folder.config(state=tk.DISABLED)