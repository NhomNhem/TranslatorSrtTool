# file_handling.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk  # Import ttk here
import os
import subprocess
import threading
import config
import translator
# NO gui import here
import sys # Import sys for resource_path


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def _read_file_lines(file_path):
    """Hàm hỗ trợ đọc dòng từ file với xử lý lỗi."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.readlines()
    except Exception as e:
        raise Exception(f"Lỗi khi mở file: {e}")

def _write_file_lines(file_path, lines):
    """Hàm hỗ trợ ghi dòng vào file với xử lý lỗi."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(lines)
    except Exception as e:
        raise Exception(f"Lỗi khi ghi file: {e}")

def _apply_color_to_srt_line(line, color):
    """Áp dụng màu cho dòng SRT."""
    if "-->" not in line and not line.strip().isdigit() and line.strip() != "":
        return f"<font color='{color}'>{line.strip()}</font>\n"
    return line

def _apply_color_to_ass_line(line, color):
    """Áp dụng màu cho dòng ASS."""
    if "Dialogue:" in line:
        parts = line.split(",", 9)
        if len(parts) > 9:
            parts[9] = parts[9].replace(r"{\\c&H[0-9a-fA-F]+&}", "") # Correct regex for ASS color tag
            parts[9] = f"{{\\c&H{color[1:]}&}}{parts[9].strip()}" # Correct color code format for ASS
            return ",".join(parts)
    return line


def apply_color(file_path, output_path, color, progress_var, file_label, open_button, format_, root):
    """Áp dụng màu cho file phụ đề (không dịch)."""
    try:
        lines = _read_file_lines(file_path)
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))
        file_label.config(text="❌ Lỗi", foreground="red")
        return

    final_lines = []
    total_lines = len(lines)
    for i, line in enumerate(lines):
        if format_ == ".srt":
            final_lines.append(_apply_color_to_srt_line(line, color))
        elif format_ == ".ass":
            final_lines.append(_apply_color_to_ass_line(line, color))
        else:
            final_lines.append(line)

        progress_var.set(int((i + 1) / total_lines * 100))
        root.update_idletasks()

    try:
        _write_file_lines(output_path, final_lines)
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))
        file_label.config(text="❌ Lỗi", foreground="red")
        return

    file_label.config(text="✅ Hoàn tất", foreground="green")
    # Cấu hình nút "Mở file"
    open_button.config(state=tk.NORMAL, command=lambda p=output_path:  translator.open_file(p))

def apply_color_to_files(file_paths, file_widgets, file_status, root, selected_format, selected_color, btn_open_folder, translated_files):
    """Áp dụng màu cho tất cả các file đã chọn."""
    if not file_paths:
        tk.messagebox.showwarning("Cảnh báo", "Vui lòng chọn file trước.")
        return
    colored_file = []
    for file_path in file_paths:
        base_name, ext = os.path.splitext(file_path)
        output_path = os.path.join(os.path.dirname(file_path),
                                   f"{base_name}_COLORED{selected_format.get()}")

        if file_path in file_widgets:
            file_frame_item = file_widgets[file_path]
            file_item_label = file_status[file_path]
            progress_var = file_frame_item.progress_var
            progress_bar = file_frame_item.progress_bar
            open_button = file_frame_item.open_button
            filename_label = file_frame_item.filename_label
        else:
            progress_var = tk.IntVar()
            file_frame_item = tk.Frame(gui.file_frame.inner_frame, bg=config.FRAME_COLOR)  # Background color to FRAME_COLOR
            file_item_label = ttk.Label(file_frame_item, text=f"🔄", foreground="#FFD700", width=8, anchor='center', background=config.FRAME_COLOR, font=config.FONT) # Set background and font
            progress_bar = ttk.Progressbar(file_frame_item, length=150, mode="determinate", variable=progress_var, style="TProgressbar") # Reduced length
            open_button = ttk.Button(file_frame_item, text="📂 Mở", state=tk.DISABLED, style='TButton') # Keep style
            filename_label = ttk.Label(file_frame_item, text=truncate_filename(os.path.basename(file_path)), foreground=config.LABEL_COLOR,
                                        wraplength=180, anchor='w', background=config.FRAME_COLOR, font=config.FONT) # Reduced wraplength, set background and font

            file_status[file_path] = file_item_label
            file_widgets[file_path] = file_frame_item
            file_frame_item.progress_var = progress_var
            file_frame_item.progress_bar = progress_bar
            file_frame_item.open_button = open_button
            file_frame_item.filename_label = filename_label
            #---- Grid layout for file items ----
            file_item_label.grid(row=0, column=0, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
            progress_bar.grid(row=0, column=1, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
            open_button.grid(row=0, column=2, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
            filename_label.grid(row=0, column=3, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
            file_frame_item.grid(sticky="ew", pady=2, padx=5, ipadx=2, ipady=1) # Adjusted padding and sticky for frame
            file_frame_item.columnconfigure(1, weight=1) # Progress bar column expands

        # Đặt lại trạng thái và progress bar
        file_item_label.config(text=f"🔄", foreground="#FFD700")  # Chỉ hiển thị icon
        progress_var.set(0)
        open_button.config(state=tk.DISABLED, command=None)  # Reset nút mở file

        # Áp dụng màu (trong thread riêng)
        threading.Thread(target=apply_color, args=(
            file_path, output_path, selected_color.get(), progress_var, file_item_label, open_button, selected_format.get(), root),
                         daemon=True).start()
        colored_file.append(output_path)

    if colored_file:
      translated_files[:] = colored_file # Cập nhật lại translated_files
      messagebox.showinfo("Thành công", "Đã áp dụng màu cho các file đã chọn.")
      btn_open_folder.config(state=tk.NORMAL, command=lambda: subprocess.Popen(
            ["explorer", os.path.dirname(colored_file[0])] if os.name == 'nt' else ["open", os.path.dirname(
                colored_file[0])]))
    else:
      messagebox.showinfo("Thông Báo", "Không có file nào được chỉnh sửa")

def start_translation(file_paths, file_frame, file_status, file_widgets, selected_format, selected_color, root,
                      stop_translation, paused, pause_event, translated_files):
    """Function to initiate and manage the subtitle translation process.""" #Docstring in English for consistency
    if not file_paths:
        tk.messagebox.showwarning("Lỗi", "Vui lòng chọn ít nhất một file.")
        return

    stop_translation = False
    paused = False
    translated_files.clear()

    # IMPORTANT: Clear existing widgets before adding new ones!
    for widget in file_frame.inner_frame.winfo_children(): # Corrected frame to clear widgets from inner_frame
        widget.destroy()

    for file_path in file_paths:
        # Tạo đường dẫn đầu ra dựa trên file_path và selected_format
        base_name, ext = os.path.splitext(file_path)
        output_path = os.path.join(os.path.dirname(file_path), f"{os.path.basename(base_name)}_VI{selected_format.get()}")

        progress_var = tk.IntVar() # Tạo biến lưu giá trị thanh tiến trình

        # Tạo một frame con trong file_frame để nhóm các widget cho file này
        file_frame_item = tk.Frame(file_frame.inner_frame, bg=config.FRAME_COLOR)  # Background color to FRAME_COLOR
        file_item_label = ttk.Label(file_frame_item, text=f"🔄", foreground="#FFD700", width=8, anchor='center', background=config.FRAME_COLOR, font=config.FONT) # Set background and font
        progress_bar = ttk.Progressbar(file_frame_item, length=150, mode="determinate", variable=progress_var, style="TProgressbar") # Reduced length
        open_button = ttk.Button(file_frame_item, text="📂 Mở", state=tk.DISABLED, style='TButton')
        filename_label = ttk.Label(file_frame_item, text=truncate_filename(os.path.basename(file_path)), foreground=config.LABEL_COLOR,
                                       wraplength=180, anchor='w', background=config.FRAME_COLOR, font=config.FONT) # Reduced wraplength, set background and font

        file_status[file_path] = file_item_label
        file_widgets[file_path] = file_frame_item

        # Thêm các thuộc tính tùy chỉnh và frame con
        file_frame_item.progress_var = progress_var
        file_frame_item.progress_bar = progress_bar
        file_frame_item.open_button = open_button
        file_frame_item.filename_label = filename_label

        #---- Grid layout for file items ----
        file_item_label.grid(row=0, column=0, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
        progress_bar.grid(row=0, column=1, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
        open_button.grid(row=0, column=2, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
        filename_label.grid(row=0, column=3, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
        file_frame_item.grid(sticky="ew", pady=2, padx=5, ipadx=2, ipady=1) # Adjusted padding and sticky for frame
        file_frame_item.columnconfigure(1, weight=1) # Progress bar column expands


        # Đặt lại trạng thái và progress bar
        file_item_label.config(text=f"🔄", foreground="#FFD700")  # Chỉ hiển thị icon
        progress_var.set(0)
        open_button.config(state=tk.DISABLED, command=None)  # Reset nút mở file

        # Bắt đầu dịch (trong thread riêng)
        threading.Thread(target=lambda : _start_translate_thread( # Sử dụng lambda để truyền thêm arguments
            file_path, output_path, selected_format.get(), selected_color.get(), progress_var, file_item_label,
            open_button, stop_translation, paused, pause_event, root
        ), daemon=True).start() # Pass selected_color.get() and root


def _start_translate_thread(file_path, output_path, format_, color, progress_var, file_item_label, open_button,
                       stop_translation, paused, pause_event, root): # Hàm hỗ trợ mới để xử lý thread dịch

    try:
        lines = _read_file_lines(file_path) # Đọc file ở file_handling
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))
        file_item_label.config(text="❌ Lỗi mở file", foreground="red")
        return

    try:
        translated_lines = translator.translate_subtitle(lines, output_path, format_, color, progress_var, file_item_label, open_button, # Gọi hàm dịch ở translator, truyền lines vào
                           stop_translation, paused, pause_event, root)
    except Exception as e: # Bắt lỗi nếu có lỗi trong quá trình dịch
        file_item_label.config(text="❌ Lỗi dịch", foreground="red")
        messagebox.showerror("Lỗi", "Đã xảy ra lỗi trong quá trình dịch.") # Thông báo lỗi chung
        return

    if translated_lines: # Chỉ ghi file nếu có kết quả dịch
        try:
            _write_file_lines(output_path, translated_lines) # Ghi file ở file_handling
            file_item_label.config(text="✅ Hoàn tất", foreground="green")
            open_button.config(state=tk.NORMAL, command=lambda p=output_path:  translator.open_file(p)) # Mở file dùng translator.open_file
        except Exception as e:
            file_item_label.config(text="❌ Lỗi ghi file", foreground="red")
            messagebox.showerror("Lỗi", str(e))
            return
    else: # Trường hợp không có dòng nào được dịch (ví dụ file rỗng, hoặc lỗi dịch ở translator)
        file_item_label.config(text="❌ Lỗi dịch", foreground="red") # hoặc "❌ File rỗng" tùy logic
        messagebox.showerror("Lỗi", "Không có nội dung nào được dịch.") # Hoặc thông báo phù hợp

def select_files(file_label, btn_translate, btn_apply_color, file_frame, file_paths, file_status, file_widgets):
    """Chọn file SRT/ASS."""
    global current_file_path  # Sử dụng biến global # Consider removing global

    file_paths_temp = filedialog.askopenfilenames(filetypes=[["Subtitle files", "*.srt *.ass"]])
    if file_paths_temp:
        file_paths.clear()  # Xóa danh sách cũ
        file_paths.extend(file_paths_temp)  # Thêm file mới
        file_label.config(text=f"📂 {len(file_paths)} file đã chọn")
        btn_translate.config(state=tk.NORMAL)
        btn_apply_color.config(state=tk.NORMAL)
        current_file_path = file_paths[0]  # Chỉ gán file đầu tiên # Consider removing

    else:  # Người dùng nhấn Cancel
        file_label.config(text="Chưa chọn file", foreground=config.LABEL_COLOR) # Set foreground here too
        btn_translate.config(state=tk.DISABLED)
        btn_apply_color.config(state=tk.DISABLED)
        current_file_path = None  # Reset biến # Consider removing
        file_paths.clear() # Xóa các file đã chọn

    # Xóa các widget hiển thị file cũ
    for widget in file_frame.inner_frame.winfo_children(): # Clear widgets from inner_frame
        widget.destroy()

    # Tạo widget mới cho các file đã chọn
    if file_paths: # Chỉ thực hiện nếu có file
        for i, file_path in enumerate(file_paths):
            progress_var = tk.IntVar()
            file_frame_item = tk.Frame(file_frame.inner_frame, bg=config.FRAME_COLOR) # Background color to FRAME_COLOR
            file_item_label = ttk.Label(file_frame_item, text=f"🔄", foreground="#FFD700", width=8, anchor='center', background=config.FRAME_COLOR, font=config.FONT) # Set background, font and anchor
            progress_bar = ttk.Progressbar(file_frame_item, length=150, mode="determinate", variable=progress_var, style="TProgressbar") # Reduced length
            open_button = ttk.Button(file_frame_item, text="📂 Mở", style='TButton', state=tk.DISABLED)
            filename_label = ttk.Label(file_frame_item, text=truncate_filename(os.path.basename(file_path)), foreground=config.LABEL_COLOR, wraplength=180, anchor='w', background=config.FRAME_COLOR, font=config.FONT) # Reduced wraplength, set background and font

            file_status[file_path] = file_item_label
            file_widgets[file_path] = file_frame_item
            file_frame_item.progress_var = progress_var  # Lưu trữ các đối tượng
            file_frame_item.progress_bar = progress_bar
            file_frame_item.open_button = open_button
            file_frame_item.filename_label = filename_label


            #---- Grid layout for file items ----
            file_item_label.grid(row=0, column=0, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
            progress_bar.grid(row=0, column=1, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
            open_button.grid(row=0, column=2, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
            filename_label.grid(row=0, column=3, padx=(0,5), pady=2, sticky="ew") # Adjusted padx
            file_frame_item.grid(sticky="ew", pady=2, padx=5, ipadx=2, ipady=1) # Adjusted padding and sticky for frame
            file_frame_item.columnconfigure(1, weight=1) # Progress bar column expands


def open_translated_folder(translated_files):
    """Mở thư mục chứa các file đã dịch/đổi màu."""
    if translated_files:
        # Mở thư mục của file đầu tiên trong danh sách
        subprocess.Popen(["explorer", os.path.dirname(translated_files[0])] if os.name == 'nt' else ["open", os.path.dirname(translated_files[0])])

def cancel_translation(stop_translation):
    """Cancels the translation process."""
    # Use messagebox for confirmation
    if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn hủy?"):
        stop_translation = True
        # You might want to add more cleanup here, depending on # Consider cleanup actions
        # what needs to be reset if the translation is cancelled mid-process.
def truncate_filename(filename, max_length=config.FILE_NAME_MAX_LENGTH):
    if len(filename) > max_length:
        return filename[:max_length - 3] + "..."
    return filename