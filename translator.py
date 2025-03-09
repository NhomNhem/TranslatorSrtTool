# translator.py
from deep_translator import GoogleTranslator, exceptions
from tkinter import messagebox  # Import ở đây, vì dùng trong open_file
import os
import subprocess
import sys # Thêm


def translate_line(translator, line, format_):
    """Dịch một dòng, xử lý các trường hợp khác nhau."""
    try:
        if format_ == ".srt":
            if "-->" not in line and not line.strip().isdigit() and line.strip() != "":
                translated_text = translator.translate(line.strip())
                return translated_text + "\n"
            else:
                return line
        elif format_ == ".ass":
            if "Dialogue:" in line:
                parts = line.split(",", 9)
                if len(parts) > 9:
                    text = parts[9].strip()
                    translated_text = translator.translate(text)
                    parts[9] = translated_text
                    return ",".join(parts)
            return line
        else:
            return line  # Trường hợp default

    except Exception as e:
        # Xử lý lỗi tổng quát, không cần re-raise
        return line  # Hoặc có thể return ""


def _apply_color_to_translated_srt_line(line, color):
    """Áp dụng màu cho dòng SRT đã dịch."""
    if "-->" not in line and not line.strip().isdigit() and line.strip() != "":
        return f"<font color='{color}'>{line.strip()}</font>\n"
    return line

def _apply_color_to_translated_ass_line(line, color):
    """Áp dụng màu cho dòng ASS đã dịch."""
    if "Dialogue:" in line:
        parts = line.split(",", 9)
        if len(parts) > 9:
            parts[9] = parts[9].replace(r"{\c&H[0-9a-fA-F]+&}", "")
            parts[9] = f"{{\\c&H{color[1:]}&}}{parts[9].strip()}"  # Bỏ #
            return ",".join(parts)
    return line


def translate_subtitle(lines, output_path, format_, color, progress_var, file_item_label, open_button,
                       stop_translation, paused, pause_event, root):
    """Hàm dịch phụ đề (được gọi trong thread) - **ĐÃ SỬA ĐỂ KHÔNG ĐỌC/GHI FILE TRỰC TIẾP**."""

    translator = GoogleTranslator(source="en", target="vi")

    translated_lines = []
    total_lines = len(lines)

    for i, line in enumerate(lines):
        if stop_translation:
            file_item_label.config(text="❌ Dịch bị hủy!", foreground="red")
            return

        if paused:
            file_item_label.config(text="⏸ Tạm dừng...", foreground="orange")
            pause_event.wait()
            file_item_label.config(text=f"🔄", foreground="#FFD700")

        try:
            translated_lines.append(translate_line(translator, line, format_))
        except Exception as e:
            file_item_label.config(text="❌ Lỗi dịch", foreground="red")
            messagebox.showerror("Lỗi dịch", str(e)) # Hiển thị lỗi cụ thể hơn
            return

        progress_var.set(int((i + 1) / total_lines * 100))
        root.update_idletasks()

    # Áp dụng màu (và định dạng) - Sử dụng hàm hỗ trợ mới
    final_lines = []
    for line in translated_lines:
        if format_ == ".srt":
            final_lines.append(_apply_color_to_translated_srt_line(line, color))
        elif format_ == ".ass":
            final_lines.append(_apply_color_to_translated_ass_line(line, color))
        else:
            final_lines.append(line)

    return final_lines # **TRẢ VỀ DANH SÁCH DÒNG ĐÃ XỬ LÝ, KHÔNG GHI FILE**


def open_file(file_path):
    """Mở file bằng ứng dụng mặc định."""
    try:
        if sys.platform == 'win32':
            os.startfile(file_path)  # Windows
        elif sys.platform == 'darwin':
            subprocess.call(('open', file_path))  # macOS
        else:
            subprocess.call(('xdg-open', file_path))  # Linux
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể mở file: {e}")