# Copyright (c) 2024 NhemNhem
# All rights reserved.
# This software is released under the MIT License.  (Ví dụ)
# See LICENSE file for details.

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from deep_translator import GoogleTranslator, exceptions
import threading
import os
import subprocess
from PIL import Image, ImageTk, ImageSequence
import time
import sys  # Thêm import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Copyright information (cho cửa sổ About và thanh trạng thái)
COPYRIGHT_NOTICE = "Copyright (c) 2024 NhemNhem. All rights reserved."

# Biến kiểm soát
stop_translation = False
paused = False
pause_event = threading.Event()
file_paths = []
translated_files = []

# Giao diện
root = tk.Tk()
root.title("SRT Translator")
root.geometry("800x800")
root.configure(bg="#2C2F33")

# Đặt icon
try:
  root.iconbitmap(resource_path("icon.ico"))  # Sử dụng resource_path
except tk.TclError:
    messagebox.showwarning("Cảnh báo", "Không tìm thấy hoặc không thể load file icon.ico. Ứng dụng sẽ chạy với icon mặc định.")

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
gif_path = resource_path("sprite/ani.gif")  # Sử dụng resource_path
try:
    gif_image = Image.open(gif_path)
    gif_frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif_image)]
    gif_index = 0
except FileNotFoundError:
    messagebox.showerror("Lỗi", "Không tìm thấy file ảnh động 'ani.gif'. Vui lòng đảm bảo file nằm trong thư mục 'sprite'.")
    root.destroy()
    sys.exit()  # Sử dụng sys.exit()

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
    about_window.title("About SRT Translator")
    about_window.geometry("400x250")
    about_window.configure(bg="#2C2F33")

    about_text = tk.Text(about_window, wrap=tk.WORD, bg="#2C2F33", fg="white", font=("Arial", 10), borderwidth=0)
    about_text.insert(tk.END, "SRT Translator\n\n")
    about_text.insert(tk.END, f"Version: 2.0\n")
    about_text.insert(tk.END, f"{COPYRIGHT_NOTICE}\n\n")
    about_text.insert(tk.END, "Developed by: NhemNhem\n")
    about_text.insert(tk.END, "Powered by: deep_translator, Tkinter, Pillow\n")

    about_text.config(state=tk.DISABLED)
    about_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

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
                    original_indices.append((j, 9))
                else:
                    translated_lines.append(line)

            elif "-->" in line or line.strip().isdigit() or line.strip() == "":
                translated_lines.append(line)
            else:
                batch_to_translate.append(line.strip())
                original_indices.append((j, -1))

        try:
            if batch_to_translate:
                translated_batch = translator.translate_batch(batch_to_translate)

                for k, translated_text in enumerate(translated_batch):
                    original_index, part_index = original_indices[k]
                    if part_index == -1:
                        if selected_format.get() == ".srt":
                            translated_lines.append(f"<font color='{selected_color.get()}'>{translated_text}</font>\n")
                        else:
                            translated_lines.append(translated_text + "\n")
                    else:
                        parts = batch[original_index].split(",", 9)
                        if selected_format.get() == ".ass":
                            parts[9] = f"{{\\c&H{selected_color.get()[1:]}&}}{translated_text}"
                        else:
                            parts[9] = translated_text
                        translated_lines.append(",".join(parts))
            else:
               for line in batch:
                    translated_lines.append(line)

        except exceptions.NotValidPayload:
            messagebox.showerror("Lỗi Dịch", "Lỗi: Quá nhiều yêu cầu.  Có thể bạn đã hết lượt dịch miễn phí.  Vui lòng thử lại sau hoặc sử dụng API trả phí.")
            file_status[file_path].config(text="❌ Lỗi dịch", foreground="red")
            return
        except exceptions.RequestError as e:
            messagebox.showerror("Lỗi Dịch", f"Lỗi kết nối: {e}. Vui lòng kiểm tra kết nối internet.")
            file_status[file_path].config(text="❌ Lỗi dịch", foreground="red")
            return
        except Exception as e:
            messagebox.showerror("Lỗi Dịch", f"Lỗi không xác định: {e}")
            file_status[file_path].config(text="❌ Lỗi dịch", foreground="red")
            return

        progress_var.set(int((i + len(batch)) / total_lines * 100))
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
            file_status[file_path].config(text=f"🔄 {os.path.basename(file_path)}", foreground="#FFD700")

    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.writelines(translated_lines)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi ghi file: {e}")
        return

    translated_files.append(output_path)
    file_status[file_path].config(text="✅ Hoàn tất", foreground="green")
    open_button.config(state=tk.NORMAL, command=lambda: subprocess.Popen(["explorer", os.path.dirname(output_path)] if os.name == 'nt' else ["open", os.path.dirname(output_path)]))


def cancel_translation():
    global stop_translation
    stop_translation = True

def start_translation():
    global stop_translation, paused, translated_files
    if not file_paths:
        messagebox.showwarning("Lỗi", "Vui lòng chọn file trước!")
        return

    stop_translation = False
    paused = False
    translated_files = []
    btn_pause.config(state=tk.NORMAL)

    for file_path in file_paths:
        progress_var = tk.IntVar()
        file_frame_item = tk.Frame(file_frame, bg="#2C2F33")
        file_label = ttk.Label(file_frame_item, text=f"🔄 {os.path.basename(file_path)}", foreground="#FFD700")
        progress_bar = ttk.Progressbar(file_frame_item, length=250, mode="determinate", variable=progress_var)
        open_button = ttk.Button(file_frame_item, text="📂 Mở", state=tk.DISABLED)

        file_status[file_path] = file_label
        file_widgets[file_path] = file_frame_item

        file_label.pack(side=tk.LEFT, padx=5)
        progress_bar.pack(side=tk.LEFT, padx=5)
        open_button.pack(side=tk.LEFT)
        file_frame_item.pack(fill=tk.X, pady=2)
        file_frame_item.lift()

        threading.Thread(target=translate_subtitle, args=(progress_var, file_label, open_button, file_path), daemon=True).start()

def select_files():
    global file_paths
    file_paths = filedialog.askopenfilenames(filetypes=[["Subtitle files", "*.srt *.ass"]])
    if file_paths:
        file_label.config(text=f"📂 {len(file_paths)} file đã chọn")
        btn_translate.config(state=tk.NORMAL)

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

file_label = ttk.Label(root, text="Chưa chọn file")
file_label.pack(pady=5)

btn_open_folder = ttk.Button(root, text="📁 Mở thư mục dịch", command=open_translated_folder)
btn_open_folder.pack()

file_frame = tk.Frame(root, bg="#2C2F33")
file_frame.pack(pady=10, fill=tk.BOTH, expand=True)

canvas = tk.Canvas(root, width=64, height=64, bg="#2C2F33")
canvas.pack()
try:
  sprite = canvas.create_image(32, 32, image=gif_frames[0])
  animate_gif()
except NameError: #xử lý lỗi nếu gif_frame chưa được định nghĩa
    pass


# Tạo thanh trạng thái (Status Bar)
status_bar = tk.Label(root, text=COPYRIGHT_NOTICE, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#23272A", fg="white")
status_bar.pack(side=tk.BOTTOM, fill=tk.X)


root.mainloop()