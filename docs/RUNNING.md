# Hướng dẫn chạy dự án ScoreFlow

Dự án gồm 3 phần chính cần chạy đồng thời:
1.  **Backend** (Python/FastAPI): Xử lý logic, API và database.
2.  **Admin Panel** (React/Vite): Trang quản trị cho Admin.
3.  **Mobile App** (React Native/Expo): Ứng dụng cho người dùng cuối.

---

## 1. Khởi động Backend
Backend chạy trên cổng `8000`.

**Bước 1: Mở terminal tại thư mục gốc và di chuyển vào folder backend**
```bash
cd backend
```

**Bước 2: Kích hoạt môi trường ảo (Virtual Environment)**
*   **Windows:**
    ```powershell
    .\.venv\Scripts\activate
    ```
*   **Mac/Linux:**
    ```bash
    source .venv/bin/activate
    ```

**Bước 3: Cài đặt thư viện (nếu chưa cài)**
```bash
pip install -r requirements.txt
```

**Bước 4: Chạy server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*   API Docs: `http://localhost:8000/docs`
*   Admin API: `http://localhost:8000/api/v1/admin`

---

## 2. Khởi động Admin Panel
Admin Web chạy trên cổng `5173`.

**Bước 1: Mở terminal **MỚI** tại thư mục gốc và di chuyển vào folder admin-panel**
```bash
cd admin-panel
```

**Bước 2: Cài đặt thư viện (nếu chưa cài)**
```bash
npm install
```

**Bước 3: Chạy Web Server**
```bash
npm run dev
```
*   Truy cập: `http://localhost:5173`
*   **Tài khoản Admin:** Cần set `is_superuser=True` trong database cho user của bạn.

---

## 3. Khởi động Mobile App
Ứng dụng chạy qua Expo Go.

**Bước 1: Mở terminal **MỚI** tại thư mục gốc của dự án (`ScoreFlow`)**

**Bước 2: Cài đặt thư viện (nếu chưa cài)**
```bash
npm install
```

**Bước 3: Chạy Expo**
```bash
npm start
# Hoặc
npx expo start
```
*   Quét mã QR bằng app **Expo Go** trên điện thoại (Android/iOS).
*   Hoặc nhấn `a` để chạy trên Android Emulator, `i` cho iOS Simulator.

---

## Lưu ý quan trọng
*   **IP Address:** Nếu chạy App trên điện thoại thật, hãy đảm bảo điện thoại và máy tính cùng mạng Wifi.
*   **Backend URL:** Trong file `src/services/ApiClient.ts` hoặc `.env` của Mobile App, hãy đổi `localhost` thành địa chỉ IP LAN của máy tính (ví dụ: `192.168.1.x`) để điện thoại kết nối được.
