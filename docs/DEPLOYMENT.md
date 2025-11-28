# 🚀 Hướng dẫn Deploy & Auto-Start Backend

Để backend luôn hoạt động mà không cần chạy thủ công, bạn có 2 lựa chọn:

## Cách 1: Deploy lên Cloud (Khuyên dùng - Chạy 24/7)
Cách này giúp backend chạy liên tục kể cả khi bạn tắt máy tính. Phù hợp nhất để App luôn có dữ liệu mới.

### Sử dụng Render (Miễn phí)
1.  Đẩy code lên **GitHub**.
2.  Truy cập [Render.com](https://render.com) và tạo tài khoản.
3.  Chọn **"New +"** -> **"Web Service"**.
4.  Kết nối với repo GitHub của bạn.
5.  Cấu hình như sau:
    *   **Root Directory**: `backend`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6.  Ở phần **Environment Variables**, thêm các biến trong file `.env` của bạn vào (API Key, Database URL, v.v.).
    *   *Lưu ý*: Với Database, bạn nên dùng một dịch vụ Cloud Database (như **Neon.tech** hoặc **Supabase**) thay vì SQLite local, vì SQLite trên Render sẽ bị reset mỗi khi deploy lại.

---

## Cách 2: Tự động chạy khi mở máy (Local)
Cách này chỉ chạy khi bạn bật máy tính. Phù hợp nếu bạn chỉ dev trên máy cá nhân.

### Bước 1: Tạo file chạy tự động
1.  Trong thư mục `backend`, tạo một file tên là `start_server.bat`.
2.  Dán nội dung sau vào (sửa lại đường dẫn cho đúng với máy bạn):

```bat
@echo off
cd /d "D:\HK7\DACN2\ScoreFlow\backend"
call .venv\Scripts\activate
start /min cmd /k "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
```

### Bước 2: Thêm vào Startup của Windows
1.  Nhấn `Windows + R`, gõ `shell:startup` và Enter.
2.  Tạo một **Shortcut** của file `start_server.bat` vừa tạo.
3.  Kéo Shortcut đó vào thư mục Startup vừa mở.

👉 Từ giờ mỗi khi khởi động máy, backend sẽ tự động chạy ngầm!
