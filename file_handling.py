import tkinter as tk
from tkinter import filedialog, messagebox, ttk  # Import ttk here
import os
import subprocess
import threading
import config
import translator
# NO gui import here

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def apply_color(file_path, output_path, color, progress_var, file_label, open_button, format_, root):
    """Áp dụng màu cho file phụ đề (không dịch)."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi mở file: {e}")
        file_label.config(text="❌ Lỗi", foreground="red")
        return

    final_lines = []
    total_lines = len(lines)
    for i, line in enumerate(lines):
        if format_ == ".srt":
            if "-->" not in line and not line.strip().isdigit() and line.strip() != "":
                final_lines.append(f"<font color='{color}'>{line.strip()}</font>\n")
            else:
                final_lines.append(line)
        elif format_ == ".ass":
            if "Dialogue:" in line:
                parts = line.split(",", 9)
                if len(parts) > 9:
                    parts[9] = parts[9].replace(r"{\c&H[0-9a-fA-F]+&}", "")
                    parts[9] = f"{{\\c&H{color[1:]}&}}{parts[9].strip()}"
                    final_lines.append(",".join(parts))
            else:
                final_lines.append(line)
        else:
            final_lines.append(line)

        progress_var.set(int((i + 1) / total_lines * 100))
        root.update_idletasks()

    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.writelines(final_lines)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi ghi file: {e}")
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
            file_frame_item = tk.Frame(gui.file_frame.inner_frame, bg="")  # Transparent background. Use inner_frame!
            file_item_label = ttk.Label(file_frame_item, text=f"🔄", foreground="#FFD700", width=10, background="")
            progress_bar = ttk.Progressbar(file_frame_item, length=200, mode="determinate", variable=progress_var, style="TProgressbar") # Set style here
            open_button = ttk.Button(file_frame_item, text="📂 Mở", state=tk.DISABLED, style='TButton') # Keep style
            filename_label = ttk.Label(file_frame_item, text=truncate_filename(os.path.basename(file_path)), foreground=config.LABEL_COLOR,
                                        wraplength=150, anchor='w', background="") # Set text color and transparent bg

            file_status[file_path] = file_item_label
            file_widgets[file_path] = file_frame_item
            file_frame_item.progress_var = progress_var
            file_frame_item.progress_bar = progress_bar
            file_frame_item.open_button = open_button
            file_frame_item.filename_label = filename_label
            #----
            file_item_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
            progress_bar.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
            open_button.grid(row=0, column=2, padx=5, pady=2)
            filename_label.grid(row=0, column=3, padx=5, pady=2, sticky="w")
            file_frame_item.grid(sticky="nsew") # Use grid here!
            file_frame_item.columnconfigure(1, weight=1)

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

    if not file_paths:
        tk.messagebox.showwarning("Lỗi", "Vui lòng chọn ít nhất một file.")
        return

    stop_translation = False
    paused = False
    translated_files.clear()

    # IMPORTANT: Clear existing widgets before adding new ones!
    for widget in file_frame.winfo_children():
        widget.destroy()

    for file_path in file_paths:
        # Tạo đường dẫn đầu ra dựa trên file_path và selected_format
        base_name, ext = os.path.splitext(file_path)
        output_path = os.path.join(os.path.dirname(file_path), f"{os.path.basename(base_name)}_VI{selected_format.get()}")

        progress_var = tk.IntVar() # Tạo biến lưu giá trị thanh tiến trình

        # Tạo một frame con trong file_frame để nhóm các widget cho file này
        file_frame_item = tk.Frame(file_frame, bg="")  # Transparent background
        file_item_label = ttk.Label(file_frame_item, text=f"🔄", foreground="#FFD700", width=10, background="")
        progress_bar = ttk.Progressbar(file_frame_item, length=200, mode="determinate", variable=progress_var, style="TProgressbar")
        open_button = ttk.Button(file_frame_item, text="📂 Mở", state=tk.DISABLED, style='TButton')
        filename_label = ttk.Label(file_frame_item, text=truncate_filename(os.path.basename(file_path)), foreground=config.LABEL_COLOR,
                                       wraplength=150, anchor='w', background="")

        # Lưu các widget vào dictionaries để quản lý sau này
        file_status[file_path] = file_item_label
        file_widgets[file_path] = file_frame_item

        # Thêm các thuộc tính tùy chỉnh và frame con
        file_frame_item.progress_var = progress_var
        file_frame_item.progress_bar = progress_bar
        file_frame_item.open_button = open_button
        file_frame_item.filename_label = filename_label

        # Sử dụng grid layout trong frame con
        file_item_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        progress_bar.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        open_button.grid(row=0, column=2, padx=5, pady=2)
        filename_label.grid(row=0, column=3, padx=5, pady=2, sticky="w")  # Cột 3
        file_frame_item.grid(sticky="nsew") # Use grid here!
        file_frame_item.columnconfigure(1, weight=1)

        progress_var.set(0)
        open_button.config(state=tk.DISABLED, command=None)
        threading.Thread(target=translator.translate_subtitle, args=(
            file_path, output_path, selected_format.get(), selected_color.get(), progress_var, file_item_label,
            open_button, stop_translation, paused, pause_event, root
        ), daemon=True).start() # Pass selected_color.get() and root

def select_files(file_label, btn_translate, btn_apply_color, file_frame, file_paths, file_status, file_widgets):
    """Chọn file SRT/ASS."""
    global current_file_path  # Sử dụng biến global

    file_paths_temp = filedialog.askopenfilenames(filetypes=[["Subtitle files", "*.srt *.ass"]])
    if file_paths_temp:
        file_paths.clear()  # Xóa danh sách cũ
        file_paths.extend(file_paths_temp)  # Thêm file mới
        file_label.config(text=f"📂 {len(file_paths)} file đã chọn")
        btn_translate.config(state=tk.NORMAL)
        btn_apply_color.config(state=tk.NORMAL)
        current_file_path = file_paths[0]  # Chỉ gán file đầu tiên

    else:  # Người dùng nhấn Cancel
        file_label.config(text="Chưa chọn file", foreground=config.LABEL_COLOR) # Set foreground here too
        btn_translate.config(state=tk.DISABLED)
        btn_apply_color.config(state=tk.DISABLED)
        current_file_path = None  # Reset biến
        file_paths.clear() # Xóa các file đã chọn

    # Xóa các widget hiển thị file cũ
    for widget in file_frame.winfo_children():
        widget.destroy()

    # Tạo widget mới cho các file đã chọn (tối đa 5 file)
    if file_paths: # Chỉ thực hiện nếu có file
        for i, file_path in enumerate(file_paths):
            # if i >= 5:  # Giới hạn hiển thị
            #     break
            progress_var = tk.IntVar()
            file_frame_item = tk.Frame(file_frame, bg="") # Transparent background
            file_item_label = ttk.Label(file_frame_item, text=f"🔄", foreground="#FFD700", width=10, background="")
            progress_bar = ttk.Progressbar(file_frame_item, length=200, mode="determinate", variable=progress_var, style="TProgressbar") # Add style here
            open_button = ttk.Button(file_frame_item, text="📂 Mở", style='TButton', state=tk.DISABLED)
            filename_label = ttk.Label(file_frame_item, text=truncate_filename(os.path.basename(file_path)), foreground=config.LABEL_COLOR, wraplength=250, anchor='w', background="")

            file_status[file_path] = file_item_label
            file_widgets[file_path] = file_frame_item
            file_frame_item.progress_var = progress_var  # Lưu trữ các đối tượng
            file_frame_item.progress_bar = progress_bar
            file_frame_item.open_button = open_button
            file_frame_item.filename_label = filename_label


            #Sử dụng grid để layout
            file_item_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
            progress_bar.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
            open_button.grid(row=0, column=2, padx=5, pady=2)
            filename_label.grid(row=0, column=3, padx=5, pady=2, sticky="w")
            file_frame_item.grid(sticky="nsew") # VERY IMPORTANT: Use grid here!
            file_frame_item.columnconfigure(1, weight=1)

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
        # You might want to add more cleanup here, depending on
        # what needs to be reset if the translation is cancelled mid-process.
def truncate_filename(filename, max_length=config.FILE_NAME_MAX_LENGTH):
    if len(filename) > max_length:
        return filename[:max_length - 3] + "..."
    return filename