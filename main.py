import tkinter as tk
from tkinter import ttk
import gui  # Import module gui
import file_handling
import config
import threading

if __name__ == "__main__":  # Main application setup - NOW IN MAIN.PY
    gui.root = tk.Tk() # Sử dụng gui.root
    gui.root.title(config.APP_NAME)  # Sử dụng gui.root
    gui.root.geometry("850x700")
    gui.root.resizable(False, False)
    gui.root.configure(bg=config.BG_COLOR)

    gui.selected_format = tk.StringVar(value=config.DEFAULT_FORMAT) # Sử dụng gui.selected_format
    gui.selected_color = tk.StringVar(value=config.DEFAULT_COLOR) # Sử dụng gui.selected_color

    file_paths = []
    stop_translation = False
    paused = False
    pause_event = threading.Event()
    pause_event.set()
    translated_files = []

    # --- Main Frame ---
    main_frame = tk.Frame(gui.root, bg=config.BG_COLOR) # Sử dụng gui.root
    main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # --- Top Buttons Frame ---
    top_buttons_frame = tk.Frame(main_frame, bg=config.BG_COLOR)
    top_buttons_frame.pack(fill=tk.X, pady=(0, 10))

    style = ttk.Style()
    style.configure('TButton', background=config.BUTTON_COLOR, foreground="black",  # <-- ĐÃ THAY ĐỔI THÀNH "black"
                    font=config.FONT, borderwidth=0, padding=5)
    style.map('TButton', background=[('active', config.BUTTON_ACTIVE_COLOR)],
              foreground=[('active', "black")])  # <-- ĐÃ THAY ĐỔI THÀNH "black" Ở ĐÂY NỮA
    style.configure("TProgressbar", foreground=config.PROGRESS_BAR_COLOR, background=config.PROGRESS_BAR_COLOR,
                    troughcolor=config.BG_COLOR)
    style.configure('Header.TLabel', font=config.HEADER_FONT, background=config.BG_COLOR,
                    foreground=config.DEFAULT_COLOR)

    btn_select = ttk.Button(top_buttons_frame, text="📂 Chọn file SRT/ASS", style='TButton',
                             command=lambda: file_handling.select_files(gui.file_label, gui.btn_translate,
                                                                        gui.btn_apply_color, gui.file_frame,
                                                                        file_paths, gui.file_status, gui.file_widgets))
    btn_select.pack(side=tk.LEFT, padx=5)

    gui.btn_translate = ttk.Button(top_buttons_frame, text="▶ Bắt đầu dịch", style='TButton', # Sử dụng gui.btn_translate
                                 command=gui.start_translation_wrapper, state=tk.DISABLED) # Sử dụng gui.start_translation_wrapper
    gui.btn_translate.pack(side=tk.LEFT, padx=5)

    gui.btn_apply_color = ttk.Button(top_buttons_frame, text="🎨 Áp dụng màu", style='TButton', # Sử dụng gui.btn_apply_color
                                  command=lambda: file_handling.apply_color_to_files(file_paths,
                                                                                     gui.file_widgets, gui.file_status,
                                                                                     gui.root, gui.selected_format, # Sử dụng gui.root, gui.selected_format
                                                                                     gui.selected_color, # Sử dụng gui.selected_color
                                                                                     gui.btn_open_folder, # Sử dụng gui.btn_open_folder
                                                                                     translated_files),
                                  state=tk.DISABLED)
    gui.btn_apply_color.pack(side=tk.LEFT, padx=5)

    gui.btn_pause = ttk.Button(top_buttons_frame, text="⏸ Tạm dừng", style='TButton', command=gui.toggle_pause_wrapper, # Sử dụng gui.btn_pause, gui.toggle_pause_wrapper
                             state=tk.DISABLED)
    gui.btn_pause.pack(side=tk.LEFT, padx=5)

    btn_cancel = ttk.Button(top_buttons_frame, text="❌ Hủy", style='TButton', command=gui.cancel_translation_wrapper) # Sử dụng gui.cancel_translation_wrapper
    btn_cancel.pack(side=tk.LEFT, padx=5)

    btn_clear = ttk.Button(top_buttons_frame, text="🗑️ Xóa", style='TButton', command=gui.clear_files) # Sử dụng gui.clear_files
    btn_clear.pack(side=tk.LEFT, padx=5)

    btn_about = ttk.Button(top_buttons_frame, text="ℹ️ About", style='TButton', command=gui.show_about) # Sử dụng gui.show_about
    btn_about.pack(side=tk.LEFT, padx=5)

    # --- Settings Frame ---
    settings_frame = tk.Frame(main_frame, bg=config.BG_COLOR)
    settings_frame.pack(fill=tk.X, pady=(0, 10))

    # --- Format Setting ---
    format_frame = tk.Frame(settings_frame, bg=config.BG_COLOR)
    format_frame.pack(side=tk.LEFT, padx=10)
    format_label = ttk.Label(format_frame, text="Định dạng:", style='Header.TLabel')
    format_label.pack(side=tk.LEFT, padx=(0, 5))
    gui.format_dropdown = ttk.Combobox(format_frame, textvariable=gui.selected_format, values=[".srt", ".ass"], font=config.FONT) # Sử dụng gui.format_dropdown, gui.selected_format
    gui.format_dropdown.pack(side=tk.LEFT)
    gui.format_dropdown.bind("<<ComboboxSelected>>", gui.on_format_change) # Sử dụng gui.on_format_change

    # --- Color Setting ---
    color_frame = tk.Frame(settings_frame, bg=config.BG_COLOR)
    color_frame.pack(side=tk.LEFT, padx=10)
    gui.color_button = ttk.Button(color_frame, text="🎨 Chọn màu chữ", style='TButton', # Sử dụng gui.color_button
                              command=lambda: gui.choose_color(gui.selected_color, gui.preview_label, gui.format_dropdown)) # Sử dụng gui.choose_color, gui.selected_color, gui.preview_label, gui.format_dropdown
    gui.color_button.pack(side=tk.LEFT, padx=(0, 5))
    gui.color_label = ttk.Label(color_frame, text=f"Màu chữ: {gui.selected_color.get()}", style='Header.TLabel') # Sử dụng gui.color_label, gui.selected_color
    gui.color_label.pack(side=tk.LEFT)

    # --- Preview Frame ---
    preview_frame = tk.Frame(main_frame, bg=config.BG_COLOR)
    preview_frame.pack(fill=tk.X, pady=(0, 10))

    preview_label_header = ttk.Label(preview_frame, text="Mẫu:", style='Header.TLabel')
    preview_label_header.pack(side=tk.LEFT, padx=10, anchor='w')
    gui.preview_label = ttk.Label(preview_frame, text="", foreground="white", background=config.BG_COLOR, # Sử dụng gui.preview_label
                              font=config.FONT, wraplength=300, anchor='w', justify=tk.LEFT)
    gui.preview_label.pack(pady=5, fill=tk.X, padx=10)


    # --- File List Frame ---
    file_list_header_frame = tk.Frame(main_frame, bg=config.BG_COLOR)
    file_list_header_frame.pack(fill=tk.X, padx=10)
    gui.file_label = ttk.Label(file_list_header_frame, text="File đã chọn:", style='Header.TLabel', anchor='w') # Sử dụng gui.file_label
    gui.file_label.pack(fill=tk.X, pady=(0, 5))

    gui.file_frame = gui.ScrolledFrame(main_frame, bg=config.FRAME_COLOR) # Sử dụng gui.file_frame, gui.ScrolledFrame
    gui.file_frame.pack(pady=(0, 10), fill=tk.BOTH, expand=True, padx=10)

    # --- File List Column Headers ---
    file_header_frame = tk.Frame(gui.file_frame.inner_frame, bg=config.FRAME_COLOR)
    file_header_frame.grid(row=0, column=0, sticky="ew", columnspan=4, padx=5, pady=2)

    header_stt = ttk.Label(file_header_frame, text="Stt", style='Header.TLabel', width=5, anchor='center')
    header_stt.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
    header_progress = ttk.Label(file_header_frame, text="Tiến trình", style='Header.TLabel', width=10, anchor='center')
    header_progress.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
    header_status = ttk.Label(file_header_frame, text="Trạng thái Mở file", style='Header.TLabel', width=15, anchor='center')
    header_status.grid(row=0, column=2, padx=5, pady=2, sticky="ew")
    header_filename = ttk.Label(file_header_frame, text="Tên", style='Header.TLabel', anchor='w')
    header_filename.grid(row=0, column=3, padx=5, pady=2, sticky="ew")

    file_header_frame.columnconfigure(3, weight=1)

    # --- Bottom Frame ---
    bottom_frame = tk.Frame(main_frame, bg=config.BG_COLOR)
    bottom_frame.pack(fill=tk.X, pady=(10, 0), padx=10)

    gui.btn_open_folder = ttk.Button(bottom_frame, text="📁 Mở thư mục", style='TButton', # Sử dụng gui.btn_open_folder
                                 command=lambda: file_handling.open_translated_folder(translated_files),
                                 state=tk.DISABLED)
    gui.btn_open_folder.pack(side=tk.LEFT, padx=5)

    btn_exit = ttk.Button(bottom_frame, text="Thoát >", style='TButton', command=gui.root.destroy) # Sử dụng gui.root.destroy
    btn_exit.pack(side=tk.RIGHT, padx=5)

    # --- Status Bar ---
    gui.status_bar = tk.Label(gui.root, text=config.COPYRIGHT_NOTICE, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#23272A", # Sử dụng gui.status_bar, gui.root
                          fg="white", font=config.FONT)
    gui.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


    gui.update_preview(gui.selected_color, gui.format_dropdown, gui.preview_label) # Sử dụng gui.update_preview, gui.selected_color, gui.format_dropdown, gui.preview_label

    gui.root.mainloop() # Sử dụng gui.root.mainloop()