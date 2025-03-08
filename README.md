# Translator SRT Tool

## 📌 Mô tả

**Translator SRT Tool** là một công cụ giúp dịch file phụ đề `.srt` từ tiếng Anh sang tiếng Việt bằng Google Translate API. Công cụ này hỗ trợ tự động hóa việc dịch nhanh chóng, giúp người dùng tiết kiệm thời gian chỉnh sửa thủ công.

## 🚀 Tính năng

- ✅ Tự động dịch file `.srt` từ tiếng Anh sang tiếng Việt.
- ✅ Giữ nguyên định dạng thời gian trong file phụ đề.
- ✅ Giao diện đồ họa đơn giản, dễ sử dụng với `Tkinter`.
- ✅ Hỗ trợ hiển thị tiến trình dịch.
- ✅ Có thể tạm dừng và tiếp tục dịch.

---

## 🛠 Cài đặt (nếu bạn không muốn cài đặt Python hãy bỏ qua bước này và [tải xuống](https://github.com/NhomNhem/TranslatorSrtTool/releases/tag/Tool)

### 1️⃣ Cài đặt thư viện cần thiết

Chạy lệnh sau để cài đặt các thư viện cần thiết:

```bash
pip install pysrt deep-translator pillow
```

### 2️⃣ Chạy Tool

Sau khi cài đặt xong, bạn có thể chạy tool bằng lệnh:

```bash
python Tool.py
```

---

## 🏗 Build file `.exe`

Nếu bạn muốn tạo file `.exe` để chạy trên Windows mà không cần Python:

```bash
pyinstaller --onefile --windowed --icon=icon.ico --add-data "sprite/ani.gif;sprite/" Tool.py
```

Sau khi hoàn tất, file `.exe` sẽ nằm trong thư mục `dist/`.

---

## 🔧 Lỗi thường gặp & Cách khắc phục

### 1️⃣ **Lỗi** `ModuleNotFoundError: No module named 'PIL'`

🔹 Cách khắc phục: Cài đặt Pillow

```bash
pip install pillow
```

### 2️⃣ **Lỗi** `FileNotFoundError: [Errno 2] No such file or directory: 'sprite/ani.gif'`

🔹 Cách khắc phục: Kiểm tra lại đường dẫn file ảnh GIF, đảm bảo nó tồn tại. Trong trường hợp này, bạn vào thư mục /dist và paste thư mục sprite vào đó. Sau đó chạy file .exe.

### 3️⃣ **Lỗi**  `RuntimeError: Too early to create image: no default root window`

🔹 Cách khắc phục: Đảm bảo `Tk()` được khởi tạo trước khi load ảnh GIF:


```python
root = tk.Tk()  # Khởi tạo Tkinter trước
...
gif_image = Image.open(gif_path)
```
---
## 💻 Hướng dẫn sử dụng

### 1️⃣ **Chọn file `.srt` cần dịch**

🔹 Bạn có thể chọn file `.srt` cần dịch bằng cách nhấn vào nút `Browse` và chọn file từ hộp thoại mở file.

### 2️⃣ **Dịch file `.srt`**

🔹 Sau khi chọn file `.srt`, sau khi chọn sẽ dịch file `.srt` từ tiếng Anh sang tiếng Việt.

### 3️⃣ **Lưu file `.srt` đã dịch**

🔹 Sau khi dịch file `.srt`, bạn được lưu vào cùng thư mục với file `.srt` gốc với tên file là `translated_` + tên file gốc.

### 4️⃣ **Mở Video**

🔹 Bạn có thể mở video bằng cách nhấn vào nút `Open Video` và chọn file video từ hộp thoại mở file.

### 5️⃣ **Hiển thị phụ đề**

🔹 Sau khi chọn file video, bạn có thể hiển thị phụ đề bằng cách nhấn vào nút `Show Subtitle`.


---

## 📥 Tải xuống

🔹 Bạn có thể tải bản phát hành mới nhất tại đây: [Tải xuống](https://github.com/NhomNhem/TranslatorSrtTool/releases/tag/Tool)

---

## 🤝 Đóng góp

Nếu bạn muốn đóng góp cho dự án, hãy gửi pull request hoặc mở issue trên GitHub.

**Contributors:**

<a href="https://github.com/NhomNhem/TranslatorSrtTool/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=NhomNhem/TranslatorSrtTool" />
</a>

---

## 📜 Giấy phép

🔹 Đây là một dự án mã nguồn mở. Bạn có thể sử dụng, chỉnh sửa và phân phối lại theo nhu cầu cá nhân.




