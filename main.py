import tkinter as tk # Redundant import, already imported at the top. Remove this.
from tkinter import ttk
import gui # Redundant import, this is gui.py
import file_handling # Redundant import in this block, already used in wrapper functions below
import config # Redundant import in this block, already imported at the top
import sys
import threading

# Wrapper functions (no changes here) # Comment helpful
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
    global file_paths, translated_files # Good to list globals being modified
    file_paths = []
    translated_files = []

    for widget in gui.file_frame.inner_frame.winfo_children(): # Corrected frame to clear widgets from inner_frame
        widget.destroy()

    gui.file_status.clear()
    gui.file_widgets.clear()

    gui.file_label.config(text="Chưa chọn file", foreground=config.LABEL_COLOR)
    gui.btn_translate.config(state=tk.DISABLED)
    gui.btn_apply_color.config(state=tk.DISABLED)
    gui.btn_open_folder.config(state=tk.DISABLED)


if __name__ == "__main__": # Main application setup is within gui.py, a bit unconventional, could be moved to a separate main.py
    root = tk.Tk()
    root.title("SRT Translator")
    root.geometry("800x800")  # Set initial size
    root.resizable(False, False)  # Disable resizing
    root.configure(bg=config.BG_COLOR)

    selected_format = tk.StringVar(value=config.DEFAULT_FORMAT)
    selected_color = tk.StringVar(value=config.DEFAULT_COLOR)

    file_paths = [] # Globals initialized here, consistent
    stop_translation = False # Globals initialized here, consistent
    paused = False # Globals initialized here, consistent
    pause_event = threading.Event() # Globals initialized here, consistent
    pause_event.set() # Globals initialized here, consistent
    translated_files = [] # Globals initialized here, consistent

    # --- Main Frame ---
    main_frame = tk.Frame(root, bg=config.BG_COLOR)
    main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # --- Top Bar (Buttons) ---
    top_frame = tk.Frame(main_frame, bg=config.BG_COLOR)
    top_frame.pack(fill=tk.X)

    style = ttk.Style()
    style.configure('TButton', background=config.BUTTON_COLOR, foreground=config.BUTTON_TEXT_COLOR, font=config.FONT, borderwidth=0) # Button_TEXT_COLOR needs fix from config
    style.map('TButton', background=[('active', config.BUTTON_ACTIVE_COLOR)], foreground=[('active', config.BUTTON_TEXT_COLOR)]) # Button_TEXT_COLOR needs fix from config
    style.configure("TProgressbar", foreground=config.PROGRESS_BAR_COLOR, background=config.PROGRESS_BAR_COLOR, troughcolor=config.BG_COLOR)


    btn_select = ttk.Button(top_frame, text="📂 Chọn file SRT/ASS", style='TButton',
                           command=lambda: file_handling.select_files(gui.file_label, gui.btn_translate, gui.btn_apply_color, gui.file_frame, file_paths, gui.file_status, gui.file_widgets))
    btn_select.pack(side=tk.LEFT, padx=5)

    btn_translate = ttk.Button(top_frame, text="▶ Bắt đầu dịch", style='TButton', command=start_translation_wrapper, state=tk.DISABLED)
    btn_translate.pack(side=tk.LEFT, padx=5)

    btn_apply_color = ttk.Button(top_frame, text="🎨 Áp dụng màu", style='TButton',
                                 command=lambda: file_handling.apply_color_to_files(file_paths,
                                                                                    gui.file_widgets, gui.file_status,
                                                                                    gui.root, selected_format,
                                                                                    selected_color,
                                                                                    gui.btn_open_folder,
                                                                                    translated_files),
                                 state=tk.DISABLED)
    btn_apply_color.pack(side=tk.LEFT, padx=5)

    btn_pause = ttk.Button(top_frame, text="⏸ Tạm dừng", style='TButton', command=toggle_pause_wrapper, state=tk.DISABLED)
    btn_pause.pack(side=tk.LEFT, padx=5)

    btn_cancel = ttk.Button(top_frame, text="❌ Hủy", style='TButton', command=cancel_translation_wrapper)
    btn_cancel.pack(side=tk.LEFT, padx=5)

    btn_clear = ttk.Button(top_frame, text="🗑️ Xóa", style='TButton', command=clear_files)
    btn_clear.pack(side=tk.LEFT, padx=5)

    btn_about = ttk.Button(top_frame, text="ℹ️ About", style='TButton', command=gui.show_about)
    btn_about.pack(side=tk.LEFT, padx=5)

    # --- Settings Frame (Format and Color) ---
    settings_frame = tk.Frame(main_frame, bg=config.BG_COLOR)
    settings_frame.pack(fill=tk.X, pady=5)

    format_label = ttk.Label(settings_frame, text="Định dạng:", background=config.BG_COLOR, foreground=config.DEFAULT_COLOR, font=config.FONT)
    format_label.pack(side=tk.LEFT, padx=(0, 5))
    format_dropdown = ttk.Combobox(settings_frame, textvariable=selected_format, values=[".srt", ".ass"], font=config.FONT)
    format_dropdown.pack(side=tk.LEFT)
    format_dropdown.bind("<<ComboboxSelected>>", on_format_change)

    color_button = ttk.Button(settings_frame, text="🎨 Chọn màu chữ", style='TButton',
                              command=lambda: gui.choose_color(selected_color, preview_label, format_dropdown))
    color_button.pack(side=tk.LEFT, padx=5)

    color_label = ttk.Label(settings_frame, text=f"Màu chữ: {selected_color.get()}", background=config.BG_COLOR, foreground=config.DEFAULT_COLOR, font=config.FONT)
    color_label.pack(side=tk.LEFT, padx=(5, 0))

     # --- Preview Label ---
    preview_label = ttk.Label(main_frame, text="", foreground="white", background=config.BG_COLOR,
                              font=config.FONT)
    preview_label.pack(pady=5, fill=tk.X)

    # --- File Label ---
    file_label = ttk.Label(main_frame, text="Chưa chọn file", background=config.BG_COLOR, foreground=config.LABEL_COLOR, font=config.FONT)
    file_label.pack(pady=5, fill=tk.X)

    # --- Scrolled Frame for Files ---
    gui.file_frame = gui.ScrolledFrame(main_frame, bg=config.FRAME_COLOR)
    gui.file_frame.pack(pady=5, fill=tk.BOTH, expand=True)

    # --- Open Folder Button ---
    btn_open_folder = ttk.Button(main_frame, text="📁 Mở thư mục", style='TButton',
                                 command=lambda: file_handling.open_translated_folder(translated_files), state=tk.DISABLED)
    btn_open_folder.pack(pady=5)

    # --- Status Bar ---
    status_bar = tk.Label(root, text=config.COPYRIGHT_NOTICE, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#23272A",
                          fg="white", font=config.FONT)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # --- Store References ---
    gui.root = root
    gui.file_label = file_label
    gui.status_bar = status_bar
    gui.btn_translate = btn_translate
    gui.btn_apply_color = btn_apply_color
    gui.btn_pause = btn_pause
    gui.color_label = color_label
    gui.preview_label = preview_label
    gui.format_dropdown = format_dropdown
    gui.color_button = color_button
    gui.selected_format = selected_format
    gui.selected_color = selected_color
    gui.btn_open_folder = btn_open_folder

    gui.update_preview(selected_color, format_dropdown, preview_label)

    root.mainloop()