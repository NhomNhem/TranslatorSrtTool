# translator.py
from deep_translator import GoogleTranslator, exceptions
from tkinter import messagebox  # Import ở đây, vì dùng trong open_file
import os
import subprocess
import sys # Thêm


def translate_line(translator, line, format_):
    """Dịch một dòng, xử lý các trường hợp khác nhau.

    Args:
        translator: Đối tượng GoogleTranslator.
        line: Dòng cần dịch.
        format_: Định dạng phụ đề (".srt" hoặc ".ass").

    Returns:
        Dòng đã dịch, hoặc dòng gốc nếu không cần dịch.
    """
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


def translate_subtitle(file_path, output_path, format_, color, progress_var, file_item_label, open_button,
                       stop_translation, paused, pause_event, root):
    """Hàm dịch phụ đề (được gọi trong thread).

    Args:
        file_path: Đường dẫn đến file phụ đề gốc.
        output_path: Đường dẫn đến file phụ đề đầu ra.
        format_: Định dạng phụ đề (".srt" hoặc ".ass").
        color: Mã màu hex (ví dụ: "#FFFFFF").
        progress_var: Biến IntVar để cập nhật tiến trình.
        file_item_label: Label để hiển thị trạng thái dịch.
        open_button: Nút để mở file sau khi dịch xong.
        stop_translation: Biến (global) để dừng quá trình dịch.
        paused: Biến (global) để tạm dừng quá trình dịch.
        pause_event: Event để xử lý tạm dừng/tiếp tục.
        root: Cửa sổ Tkinter gốc.
    """

    translator = GoogleTranslator(source="en", target="vi")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        file_item_label.config(text="❌ Không tìm thấy", foreground="red")
        return
    except Exception as e:
        file_item_label.config(text="❌ Lỗi mở file", foreground="red")
        return

    if not lines:
        file_item_label.config(text="❌ File rỗng", foreground="red")
        return

    translated_lines = []
    total_lines = len(lines)

    for i, line in enumerate(lines):
        if stop_translation:
            file_item_label.config(text="❌ Dịch bị hủy!", foreground="red")
            try:
                os.remove(output_path)
            except OSError:
                pass
            return

        if paused:
            file_item_label.config(text="⏸ Tạm dừng...", foreground="orange")
            pause_event.wait()
            file_item_label.config(text=f"🔄", foreground="#FFD700")

        try:
            translated_lines.append(translate_line(translator, line, format_))
        except Exception as e:
            file_item_label.config(text="❌ Lỗi dịch", foreground="red")
            # Có thể log lỗi e vào một file, hoặc hiển thị chi tiết hơn nếu cần
            return

        progress_var.set(int((i + 1) / total_lines * 100))
        root.update_idletasks()

    # Áp dụng màu (và định dạng)
    final_lines = []
    for line in translated_lines:
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
                    parts[9] = f"{{\\c&H{color[1:]}&}}{parts[9].strip()}"  # Bỏ #
                    final_lines.append(",".join(parts))
            else:  # Trường hợp default (không nên xảy ra)
                final_lines.append(line)
        else:
            final_lines.append(line)

    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.writelines(final_lines)
        file_item_label.config(text="✅ Hoàn tất", foreground="green")
        open_button.config(state=tk.NORMAL, command=lambda p=output_path: open_file(p))
    except Exception as e:
        file_item_label.config(text="❌ Lỗi ghi file", foreground="red")
        return


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