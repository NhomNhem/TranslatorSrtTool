import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from deep_translator import GoogleTranslator
import threading
import os
import subprocess
from PIL import Image, ImageTk, ImageSequence

# Biến kiểm soát trạng thái dịch
stop_translation = False
paused = False
current_index = 0  
file_path = ""
output_path = ""
translated_lines = []
total_lines = 0

# Giao diện chính
root = tk.Tk()
root.title("SRT Translator")
root.geometry("400x400")

# Load GIF sau khi root đã được tạo
gif_path = "sprite/ani.gif"  # Đường dẫn tới GIF
gif_image = Image.open(gif_path)
gif_frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif_image)]
gif_index = 0

# Hàm animation GIF
def animate_gif():
    global gif_index
    gif_index = (gif_index + 1) % len(gif_frames)
    canvas.itemconfig(sprite, image=gif_frames[gif_index])
    root.after(100, animate_gif)  # Đổi frame mỗi 100ms

# Hàm dịch file
def translate_srt(progress_var, progress_label):
    global stop_translation, paused, current_index, translated_lines, total_lines

    translator = GoogleTranslator(source="en", target="vi")

    while current_index < total_lines:
        if stop_translation:
            progress_label.config(text="Dịch bị hủy!")
            return
        if paused:
            progress_label.config(text="Tạm dừng...")
            return

        line = lines[current_index]
        if "-->" in line or line.strip().isdigit() or line.strip() == "":
            translated_lines[current_index] = line
        else:
            translated_lines[current_index] = translator.translate(line.strip()) + "\n"

        # Cập nhật tiến trình
        progress_percent = int((current_index + 1) / total_lines * 100)
        progress_var.set(progress_percent)
        progress_label.config(text=f"Đang dịch: {progress_percent}%")
        root.update_idletasks()

        current_index += 1

    with open(output_path, "w", encoding="utf-8") as file:
        file.writelines(translated_lines)

    messagebox.showinfo("Hoàn tất", "Dịch thành công! File đã được lưu.")
    progress_label.config(text="Hoàn tất!")

    # Hiển thị nút mở file
    btn_open_file.pack(pady=5)
    btn_stop.pack_forget()  

# Chạy dịch trên luồng khác
def start_translation():
    global stop_translation, paused, current_index, file_path, output_path, lines, translated_lines, total_lines

    file_path = filedialog.askopenfilename(filetypes=[("Subtitle files", "*.srt")])
    if not file_path:
        return

    output_path = file_path.replace(".srt", "_VI.srt")

    # Đọc file
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    translated_lines = [""] * len(lines)
    total_lines = len(lines)
    current_index = 0  

    # Hiển thị thanh tiến trình & nút dừng
    progress_var.set(0)
    progress_label.config(text="Bắt đầu dịch...")
    progress_bar.pack(pady=5)
    progress_label.pack(pady=5)
    btn_stop.pack(pady=5)
    btn_resume.pack_forget()
    btn_open_file.pack_forget()

    # Chạy dịch trên luồng khác
    stop_translation = False
    paused = False
    threading.Thread(target=translate_srt, args=(progress_var, progress_label), daemon=True).start()

# Hàm dừng dịch
def stop_translation_process():
    global paused
    paused = True
    progress_label.config(text="Đã tạm dừng!")
    btn_resume.pack(pady=5)  

# Hàm tiếp tục dịch
def resume_translation():
    global paused
    paused = False
    btn_resume.pack_forget()
    threading.Thread(target=translate_srt, args=(progress_var, progress_label), daemon=True).start()

# Hàm mở file đã dịch
def open_translated_file():
    if output_path and os.path.exists(output_path):
        subprocess.run(["explorer", os.path.abspath(output_path)])

# Thoát ứng dụng
def exit_app():
    root.quit()

frame = tk.Frame(root)
frame.pack(pady=20)

btn_translate = tk.Button(frame, text="Chọn file SRT để dịch", command=start_translation)
btn_translate.pack()

btn_stop = tk.Button(root, text="Dừng dịch", command=stop_translation_process)
btn_stop.pack_forget()  

btn_resume = tk.Button(root, text="Tiếp tục dịch", command=resume_translation)
btn_resume.pack_forget()  

btn_open_file = tk.Button(root, text="Mở file đã dịch", command=open_translated_file)
btn_open_file.pack_forget()  

btn_exit = tk.Button(root, text="Thoát", command=exit_app)
btn_exit.pack(pady=10)

# Thanh tiến trình & Label hiển thị %
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, length=300, mode="determinate", variable=progress_var)
progress_label = tk.Label(root, text="")

# Canvas hiển thị GIF
canvas = tk.Canvas(root, width=64, height=64)
canvas.pack()
sprite = canvas.create_image(32, 32, image=gif_frames[0])  
animate_gif()  

root.mainloop()
