import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from deep_translator import GoogleTranslator, exceptions
import threading
import os
import subprocess
from PIL import Image, ImageTk, ImageSequence
import time
import sys

if sys.platform == 'win32':
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- ScrolledFrame (Custom Widget) ---
class ScrolledFrame(tk.Frame):
    """A scrollable frame using a canvas and scrollbars."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Create canvas and scrollbars
        self.canvas = tk.Canvas(self, bg="#2C2F33", highlightthickness=0)
        self.scrollbar_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                        troughcolor="#23272A", bg="#7289DA", activebackground="#99AAB5",
                                        width=12)
        self.scrollbar_x = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview,
                                         troughcolor="#23272A", bg="#7289DA", activebackground="#99AAB5",
                                        width=12)
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # Pack
        self.scrollbar_y.pack(side="right", fill="y")
        # self.scrollbar_x.pack(side="bottom", fill="x") # Ẩn thanh cuộn ngang
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create inner frame
        self.inner_frame = tk.Frame(self.canvas, bg="#2C2F33")
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Bind events
        self.inner_frame.bind("<Configure>", self._configure_inner_frame)
        self.canvas.bind("<Configure>", self._configure_canvas)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
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
        # Cuộn nhanh hơn
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")


# Copyright information
COPYRIGHT_NOTICE = "Copyright (c) 2024 NhemNhem. All rights reserved."

# Biến kiểm soát
stop_translation = False
paused = False
pause_event = threading.Event()
file_paths = []
translated_files = []
current_file_path = None


# Giao diện
root = tk.Tk()
root.title("SRT Translator")
root.geometry("800x800")
root.configure(bg="#2C2F33")

# Icon
try:
    root.iconbitmap(resource_path("icon.ico"))
except tk.TclError:
    messagebox.showwarning("Cảnh báo", "Không tìm thấy icon.ico")

selected_format = tk.StringVar(root, value=".srt")
selected_color = tk.StringVar(root, value="#FFFFFF")

file_status = {}
file_widgets = {}


style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Arial", 12), padding=5, background="#7289DA", foreground="white")
style.configure("TLabel", font=("Arial", 11), background="#2C2F33", foreground="white")
style.configure("TProgressbar", thickness=10, troughcolor="#99AAB5", background="#7289DA")

# Load ảnh động
gif_path = resource_path("sprite/ani.gif")
try:
    gif_image = Image.open(gif_path)
    gif_frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif_image)]
    gif_index = 0
except FileNotFoundError:
    messagebox.showerror("Lỗi", "Không tìm thấy ani.gif")
    root.destroy()
    sys.exit()

def animate_gif():
    global gif_index
    gif_index = (gif_index + 1) % len(gif_frames)
    canvas.itemconfig(sprite, image=gif_frames[gif_index])
    root.after(100, animate_gif)

def choose_color():
    color_code = colorchooser.askcolor(title="Chọn màu chữ")
    if color_code[1]:
        selected_color.set(color_code[1])
        color_label.config(text=f"Màu chữ: {selected_color.get()}")

def change_color_only():
    choose_color()

def toggle_pause():
    global paused
    paused = not paused
    if paused:
        btn_pause.config(text="▶ Tiếp tục")
        pause_event.clear()
    else:
        btn_pause.config(text="⏸ Tạm dừng")
        pause_event.set()

def show_about():
    about_window = tk.Toplevel(root)
    about_window.title("About")
    about_window.geometry("400x250")
    about_window.configure(bg="#2C2F33")
    about_text = tk.Text(about_window, wrap=tk.WORD, bg="#2C2F33", fg="white", font=("Arial", 10), borderwidth=0)
    about_text.insert(tk.END, "SRT Translator\n\nVersion: 2.0\n" + COPYRIGHT_NOTICE + "\n\nDeveloped by: NhemNhem\nPowered by: deep_translator, Tkinter, Pillow\n")
    about_text.config(state=tk.DISABLED)
    about_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

def apply_color(file_path, output_path, color, progress_var, file_label, open_button):
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
        if selected_format.get() == ".srt":
            if "-->" not in line and not line.strip().isdigit() and line.strip() != "":
                final_lines.append(f"<font color='{color}'>{line.strip()}</font>\n")
            else:
                final_lines.append(line)
        elif selected_format.get() == ".ass":
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
    open_button.config(state=tk.NORMAL, command=lambda p=output_path: open_file(p))


def open_file(file_path):
    """Mở file bằng ứng dụng mặc định của hệ điều hành."""
    try:
        if sys.platform == 'win32':
            os.startfile(file_path)  # Windows
        elif sys.platform == 'darwin':
            subprocess.call(('open', file_path))  # macOS
        else:  # 'linux', 'linux2', etc.
            subprocess.call(('xdg-open', file_path))  # Linux
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể mở file: {e}")

def apply_color_to_files():
    """Áp dụng màu cho tất cả các file đã chọn."""
    global file_paths, translated_files

    if not file_paths:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn file trước khi áp dụng màu.")
        return

    colored_files = []
    current_color = selected_color.get()

    for file_path in file_paths:
        base_name, ext = os.path.splitext(file_path)
        output_path = os.path.join(os.path.dirname(file_path), f"{os.path.basename(base_name)}_COLORED{selected_format.get()}")

        # Tạo/lấy các widget cho file này
        if file_path in file_widgets:
            file_frame_item = file_widgets[file_path]
            file_label = file_status[file_path]
            progress_var = file_frame_item.progress_var
            progress_bar = file_frame_item.progress_bar
            open_button = file_frame_item.open_button # Lấy nút mở file
            filename_label = file_frame_item.filename_label # Lấy label tên file
        else:
            progress_var = tk.IntVar()
            file_frame_item = tk.Frame(file_frame, bg="#2C2F33")
            file_label = ttk.Label(file_frame_item, text=f"🔄", foreground="#FFD700", width=10)
            progress_bar = ttk.Progressbar(file_frame_item, length=200, mode="determinate", variable=progress_var)
            open_button = ttk.Button(file_frame_item, text="📂 Mở", state=tk.DISABLED)
            # Đặt tên file ở đây, sau khi tạo
            filename_label = ttk.Label(file_frame_item, text=os.path.basename(file_path), foreground="white", wraplength=200, anchor='w')

            file_status[file_path] = file_label
            file_widgets[file_path] = file_frame_item
            file_frame_item.progress_var = progress_var
            file_frame_item.progress_bar = progress_bar
            file_frame_item.open_button = open_button
            file_frame_item.filename_label = filename_label  # Lưu label tên file


            file_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
            progress_bar.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
            open_button.grid(row=0, column=2, padx=5, pady=2)
            filename_label.grid(row=0, column=3, padx=5, pady=2, sticky="w") # Cột 3
            file_frame_item.pack(fill=tk.X, pady=2)
            file_frame_item.columnconfigure(1, weight=1)

        # Đặt lại trạng thái và progress bar
        file_label.config(text=f"🔄", foreground="#FFD700")  # Chỉ hiển thị icon
        progress_var.set(0)
        open_button.config(state=tk.DISABLED, command=None) # Reset nút mở file

        # Áp dụng màu (trong thread riêng)
        threading.Thread(target=apply_color, args=(file_path, output_path, current_color, progress_var, file_label, open_button), daemon=True).start()
        colored_files.append(output_path)

    if colored_files:
      translated_files = colored_files
      messagebox.showinfo("Thành công", "Đã áp dụng màu cho các file đã chọn.")
      btn_open_folder.config(state=tk.NORMAL, command=lambda: subprocess.Popen(["explorer", os.path.dirname(colored_files[0])] if os.name == 'nt' else ["open", os.path.dirname(colored_files[0])]))
    else:
      messagebox.showinfo("Thông Báo", "Không có file nào được chỉnh sửa")



def translate_subtitle(progress_var, file_label, open_button, file_path):
    global stop_translation, paused, translated_files

    translator = GoogleTranslator(source="en", target="vi")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        messagebox.showerror("Lỗi", f"Không tìm thấy file: {file_path}")
        return
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi mở file: {e}")
        return

    if not lines:
        messagebox.showwarning("Lỗi", f"File {file_path} rỗng!")
        return

    batch_size = 20
    translated_lines = []
    base_name, ext = os.path.splitext(file_path)
    output_path = os.path.join(os.path.dirname(file_path), f"{os.path.basename(base_name)}_VI{selected_format.get()}")

    for i in range(0, len(lines), batch_size):
        batch = lines[i:i + batch_size]
        batch_to_translate = []
        original_indices = []

        for j, line in enumerate(batch):
          if "Dialogue:" in line:
            parts = line.split(",", 9)
            if len(parts) > 9:
              text = parts[9].strip()
              batch_to_translate.append(text)
              original_indices.append((j,9))
            else:
              translated_lines.append(line)
          elif "-->" in line or line.strip().isdigit() or line.strip() == "":
            translated_lines.append(line)

          else:
            batch_to_translate.append(line.strip())
            original_indices.append((j,-1))
        try:
            if batch_to_translate:
              translated_batch = translator.translate_batch(batch_to_translate)

              for k, translated_text in enumerate(translated_batch):
                original_index, part_index = original_indices[k]
                if part_index == -1:
                    translated_lines.append(translated_text + "\n")
                else:
                  parts = batch[original_index].split(",",9)
                  parts[9] = translated_text
                  translated_lines.append(",".join(parts))
            else:
              for line in batch:
                translated_lines.append(line)

        except exceptions.NotValidPayload:
            messagebox.showerror("Lỗi Dịch", "Quá nhiều yêu cầu, thử lại sau.")
            file_status[file_path].config(text="❌ Lỗi dịch", foreground="red")
            return
        except exceptions.RequestError as e:
            messagebox.showerror("Lỗi Dịch", f"Lỗi kết nối: {e}.")
            file_status[file_path].config(text="❌ Lỗi dịch", foreground="red")
            return
        except Exception as e:
            messagebox.showerror("Lỗi Dịch", f"Lỗi: {e}")
            file_status[file_path].config(text="❌ Lỗi dịch", foreground="red")
            return

        progress_var.set(int((i + len(batch)) / len(lines) * 100))
        root.update_idletasks()

        if stop_translation:
            file_status[file_path].config(text="❌ Dịch bị hủy!", foreground="red")
            try:
                os.remove(output_path)
            except OSError:
                pass
            return

        if paused:
            file_status[file_path].config(text="⏸ Tạm dừng...", foreground="orange")
            pause_event.wait()
            file_status[file_path].config(text=f"🔄", foreground="#FFD700")  # Không hiển thị tên file

    # Áp dụng màu sau khi dịch
    current_color = selected_color.get()
    final_lines = []
    for line in translated_lines:
        if selected_format.get() == ".srt":
             if "-->" not in line and not line.strip().isdigit() and line.strip() != "":
                final_lines.append(f"<font color='{current_color}'>{line.strip()}</font>\n")
             else:
                final_lines.append(line)

        elif selected_format.get() == ".ass":
            if "Dialogue:" in line:
                parts = line.split(",", 9)
                if len(parts) >9:
                    parts[9] = parts[9].replace(r"{\c&H[0-9a-fA-F]+&}", "")
                    parts[9] = f"{{\\c&H{current_color[1:]}&}}{parts[9].strip()}"
                    final_lines.append(",".join(parts))
            else:
                final_lines.append(line)
        else:
            final_lines.append(line)


    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.writelines(final_lines)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi ghi file: {e}")
        return

    translated_files.append(output_path)
    file_status[file_path].config(text="✅ Hoàn tất", foreground="green")
    open_button.config(state=tk.NORMAL, command=lambda p=output_path: open_file(p))


def cancel_translation():
    global stop_translation
    stop_translation = True

def start_translation():
    global stop_translation, paused, translated_files, current_file_path
    if not file_paths:
        messagebox.showwarning("Lỗi", "Vui lòng chọn file!")
        return

    stop_translation = False
    paused = False
    translated_files = []
    btn_pause.config(state=tk.NORMAL)
    btn_apply_color.config(state=tk.NORMAL)

    current_file_path = None

    for file_path in file_paths:
        progress_var = tk.IntVar()
        file_frame_item = tk.Frame(file_frame, bg="#2C2F33")
        file_item_label = ttk.Label(file_frame_item, text=f"🔄", foreground="#FFD700", width=10)
        progress_bar = ttk.Progressbar(file_frame_item, length=200, mode="determinate", variable=progress_var)
        open_button = ttk.Button(file_frame_item, text="📂 Mở", state=tk.DISABLED)
        filename_label = ttk.Label(file_frame_item, text=os.path.basename(file_path), foreground="white", wraplength=200, anchor='w')

        file_status[file_path] = file_item_label
        file_widgets[file_path] = file_frame_item
        file_frame_item.progress_var = progress_var
        file_frame_item.progress_bar = progress_bar
        file_frame_item.open_button = open_button
        file_frame_item.filename_label = filename_label


        file_item_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        progress_bar.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        open_button.grid(row=0, column=2, padx=5, pady=2)
        filename_label.grid(row=0, column=3, padx=5, pady=2, sticky="w") # Cột 3
        file_frame_item.pack(fill=tk.X, pady=2)
        file_frame_item.columnconfigure(1, weight=1)


        threading.Thread(target=translate_subtitle, args=(progress_var, file_item_label, open_button, file_path), daemon=True).start()

def select_files():
    global file_paths, current_file_path

    file_paths = filedialog.askopenfilenames(filetypes=[["Subtitle files", "*.srt *.ass"]])
    # Cập nhật label tổng quát *trước* khi xóa/thêm widget
    if file_paths:
        file_label.config(text=f"📂 {len(file_paths)} file đã chọn")
        btn_translate.config(state=tk.NORMAL)
        btn_apply_color.config(state=tk.NORMAL)
        current_file_path = file_paths[0]  # Giữ file đầu tiên cho mục đích khác, nếu cần

    else:
        file_label.config(text="Chưa chọn file")  # Đặt lại label
        btn_translate.config(state=tk.DISABLED)
        btn_apply_color.config(state=tk.DISABLED)
        current_file_path = None

    # Xóa các file hiển thị cũ *trước khi* thêm file mới
    for widget in file_frame.winfo_children():
        widget.destroy()

    # Thêm các file mới vào ScrolledFrame
    if file_paths:  # Chỉ thêm *nếu* có file được chọn
        for i, file_path in enumerate(file_paths):
            if i >= 5:  # Giới hạn hiển thị ban đầu
                break
            progress_var = tk.IntVar()
            file_frame_item = tk.Frame(file_frame, bg="#2C2F33")
            file_item_label = ttk.Label(file_frame_item, text=f"🔄", foreground="#FFD700", width=10)
            progress_bar = ttk.Progressbar(file_frame_item, length=200, mode="determinate", variable=progress_var)
            open_button = ttk.Button(file_frame_item, text="📂 Mở", state=tk.DISABLED)
            filename_label = ttk.Label(file_frame_item, text=os.path.basename(file_path), foreground="white", wraplength=200, anchor='w')

            file_status[file_path] = file_item_label
            file_widgets[file_path] = file_frame_item
            file_frame_item.progress_var = progress_var
            file_frame_item.progress_bar = progress_bar
            file_frame_item.open_button = open_button
            file_frame_item.filename_label = filename_label

            # Sử dụng grid để bố trí trong file_frame_item
            file_item_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
            progress_bar.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
            open_button.grid(row=0, column=2, padx=5, pady=2)
            filename_label.grid(row=0, column=3, padx=5, pady=2, sticky="w")  # Cột 3

            file_frame_item.pack(fill=tk.X, pady=2)
            file_frame_item.columnconfigure(1, weight=1)  # Cột progress bar mở rộng

def open_translated_folder():
    if translated_files:
        subprocess.Popen(["explorer", os.path.dirname(translated_files[0])] if os.name == 'nt' else ["open", os.path.dirname(translated_files[0])])

def exit_app():
    root.quit()

# --- GUI Layout ---
frame = tk.Frame(root, bg="#2C2F33")
frame.pack(pady=20)

btn_select = ttk.Button(frame, text="📂 Chọn file SRT/ASS", command=select_files)
btn_select.pack(side=tk.LEFT, padx=5)

btn_translate = ttk.Button(frame, text="▶ Bắt đầu dịch", command=start_translation, state=tk.DISABLED)
btn_translate.pack(side=tk.LEFT, padx=5)

btn_apply_color = ttk.Button(frame, text="🎨 Áp dụng màu", command=apply_color_to_files, state=tk.DISABLED)
btn_apply_color.pack(side=tk.LEFT, padx=5)

btn_change_color = ttk.Button(frame, text="🎨 Chỉnh màu", command=change_color_only)
btn_change_color.pack(side=tk.LEFT, padx=5)

btn_pause = ttk.Button(frame, text="⏸ Tạm dừng", command=toggle_pause, state=tk.DISABLED)
btn_pause.pack(side=tk.LEFT, padx=5)

btn_cancel = ttk.Button(frame, text="❌ Hủy", command=cancel_translation)
btn_cancel.pack(side=tk.LEFT, padx=5)

btn_about = ttk.Button(frame, text="ℹ️ About", command=show_about)
btn_about.pack(side=tk.LEFT, padx=5)

format_label = ttk.Label(root, text="Định dạng:")
format_label.pack()
format_dropdown = ttk.Combobox(root, textvariable=selected_format, values=[".srt", ".ass"])
format_dropdown.pack()

color_button = ttk.Button(root, text="🎨 Chọn màu chữ", command=choose_color)
color_button.pack()

color_label = ttk.Label(root, text=f"Màu chữ: {selected_color.get()}")
color_label.pack()

file_label = ttk.Label(root, text="Chưa chọn file")  # Label chính, biến toàn cục
file_label.pack(pady=5)

btn_open_folder = ttk.Button(root, text="📁 Mở thư mục", command=open_translated_folder)
btn_open_folder.pack()

# Sử dụng ScrolledFrame
file_frame = ScrolledFrame(root)
file_frame.pack(pady=10, fill=tk.BOTH, expand=True)
file_frame = file_frame.inner_frame


canvas = tk.Canvas(root, width=64, height=64, bg="#2C2F33", highlightthickness=0)
canvas.pack()

try:
    sprite = canvas.create_image(32, 32, image=gif_frames[0])
    animate_gif()
except NameError:
    pass

status_bar = tk.Label(root, text=COPYRIGHT_NOTICE, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#23272A", fg="white")
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
