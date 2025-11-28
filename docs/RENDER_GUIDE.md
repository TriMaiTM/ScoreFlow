# ☁️ Hướng dẫn Deploy Backend lên Render

Render là nền tảng Cloud Hosting miễn phí tốt nhất hiện nay cho Python/FastAPI. Dưới đây là các bước chi tiết để đưa backend của bạn lên sóng.

## Bước 1: Chuẩn bị Database (PostgreSQL)
Vì Render reset ổ cứng sau mỗi lần deploy, bạn **KHÔNG THỂ** dùng SQLite (`sql_app.db`). Bạn cần một PostgreSQL database online.

1.  Truy cập [Supabase.com](https://supabase.com) và tạo tài khoản.
2.  Nhấn **"New Project"**.
3.  Đặt tên Project và **đặt mật khẩu Database** (Nhớ kỹ mật khẩu này!).
4.  Chờ vài phút để Project khởi tạo xong.
5.  Vào mục **Project Settings** (biểu tượng bánh răng) -> **Database**.
6.  Kéo xuống phần **Connection String**, chọn tab **URI**.
7.  **QUAN TRỌNG**: Bỏ chọn ô **"Use connection pooling"** (để lấy port 5432) nếu kết nối bị lỗi `Network is unreachable`.
    *   Link thường có dạng: `postgresql://postgres.xxxx:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres`
8.  Copy chuỗi kết nối đó.
9.  Thay thế `[YOUR-PASSWORD]` bằng mật khẩu thật của bạn.

## Bước 2: Cấu hình Render
1.  Đẩy code lên GitHub (nếu chưa).
2.  Truy cập [Render Dashboard](https://dashboard.render.com).
3.  Nhấn **New +** -> chọn **Web Service**.
4.  Kết nối với Repository GitHub của bạn.

## Bước 3: Điền thông tin Deploy
Điền các mục như sau:

| Mục | Giá trị |
| :--- | :--- |
| **Name** | `scoreflow-backend` (hoặc tùy ý) |
| **Region** | `Singapore` (cho nhanh) |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

## Bước 4: Cài đặt Environment Variables
Kéo xuống phần **Environment Variables**, nhấn **Add Environment Variable** và thêm các biến sau (lấy từ file `.env` của bạn):

| Key | Value |
| :--- | :--- | 
| `DATABASE_URL` | *(Dán link PostgreSQL từ Bước 1 vào đây)* |
| `DATABASE_URL_ASYNC` | *(Dán link PostgreSQL từ Bước 1 vào đây)* |
| `FOOTBALL_API_KEY` | *(API Key của bạn)* |
| `SECRET_KEY` | *(Chuỗi ngẫu nhiên bất kỳ)* |
| `ENABLE_SCHEDULER` | `true` |
| `PYTHON_VERSION` | `3.11.0` (Optional, để Render dùng đúng version) |

> **Lưu ý quan trọng**: Render thường cung cấp link database bắt đầu bằng `postgres://`. Code của bạn đã được mình cập nhật để tự động xử lý cái này, nên cứ paste nguyên xi vào là được.

## Bước 5: Deploy & Tận hưởng
1.  Nhấn **Create Web Service**.
2.  Chờ khoảng 2-3 phút để Render cài đặt và khởi động.
3.  Khi thấy log báo `Application startup complete`, backend của bạn đã online! 🚀

## Bước 6: Seed dữ liệu trên Cloud
Sau khi deploy xong, database trên cloud đang trống trơn. Bạn cần seed dữ liệu cho nó.
Render có tính năng **Shell** (Console) ngay trên web.

1.  Vào tab **Shell** trong dashboard của service vừa tạo.
2.  Gõ lệnh seed:
    ```bash
    python -m app.cli seed
    ```
3.  Đợi nó chạy xong là App của bạn có dữ liệu!

---
## ⚠️ Xử lý lỗi thường gặp

### Lỗi `Network is unreachable` hoặc `Connection refused`
Lỗi này thường do Supabase chặn kết nối hoặc sai Port.
1.  Vào Supabase -> Project Settings -> Database.
2.  Bỏ tick **"Use connection pooling"**.
3.  Copy lại Connection String (lúc này Port sẽ là **5432** thay vì 6543).
4.  Cập nhật lại biến `DATABASE_URL` và `DATABASE_URL_ASYNC` trên Render.
5.  Redeploy lại.
