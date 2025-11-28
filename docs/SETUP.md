# 🚀 Hướng dẫn khởi chạy ScoreFlow

## 📋 Yêu cầu hệ thống

### Bắt buộc:
- **Node.js** 18+ và npm/yarn
- **Python** 3.11+
- **Docker Desktop** (để chạy PostgreSQL + Redis)
- **Expo Go** app trên điện thoại (hoặc Android Emulator/iOS Simulator)

### Tùy chọn:
- Android Studio (cho Android Emulator)
- Xcode (cho iOS Simulator - chỉ trên macOS)

---

## 🎯 PHẦN 1: BACKEND (FastAPI)

### Bước 1: Cài đặt Docker Desktop
1. Download tại: https://www.docker.com/products/docker-desktop
2. Cài đặt và khởi động Docker Desktop
3. Kiểm tra: 
```bash
docker --version
docker-compose --version
```

### Bước 2: Khởi động Database & Redis
```bash
# Mở PowerShell tại thư mục gốc dự án
cd d:\HK7\DACN2\ScoreFlow

# Khởi động PostgreSQL + Redis
docker-compose up -d postgres redis

# Kiểm tra containers đã chạy
docker-compose ps
```

Bạn sẽ thấy:
- `scoreflow_db` (PostgreSQL) - Port 5432
- `scoreflow_redis` (Redis) - Port 6379

### Bước 3: Setup Python Backend
```bash
# Di chuyển vào thư mục backend
cd backend

# Tạo virtual environment
python -m venv .venv

# Kích hoạt virtual environment
.venv\Scripts\Activate.ps1

# Nếu gặp lỗi ExecutionPolicy, chạy:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Cài đặt dependencies
pip install -r requirements.txt
```

### Bước 4: Cấu hình Environment Variables
```bash
# Copy file .env.example
copy .env.example .env

# Mở file .env và sửa:
# 1. DATABASE_URL_ASYNC=postgresql+asyncpg://scoreflow:password@localhost:5432/scoreflow
# 2. REDIS_URL=redis://localhost:6379/0
# 3. SECRET_KEY=<tạo random key bằng: python -c "import secrets; print(secrets.token_hex(32))">
# 4. FOOTBALL_API_KEY=<đăng ký tại https://www.football-data.org/>
```

### Bước 5: Lấy API Key (Miễn phí)
1. Truy cập: https://www.football-data.org/
2. Click "Register" → Đăng ký tài khoản
3. Vào "API" → Copy API Key
4. Paste vào file `.env`: `FOOTBALL_API_KEY=your_key_here`

**Lưu ý:** Free tier có giới hạn 10 requests/phút

### Bước 6: Tạo Database Tables
```bash
# Vẫn trong thư mục backend với .venv đã activate

# Tạo tất cả tables trong database
python init_db.py
```

### Bước 7: Seed Database với dữ liệu thật
```bash
# Đồng bộ các giải đấu phổ biến
python -m app.cli sync-leagues

# Đồng bộ lịch thi đấu (Premier League, 7 ngày tiếp theo)
python -m app.cli sync-matches 2021 7

# Hoặc seed tất cả cùng lúc
python -m app.cli seed
```

Các league_id phổ biến:
- 2021: Premier League (England)
- 2014: La Liga (Spain)
- 2002: Bundesliga (Germany)
- 2019: Serie A (Italy)
- 2015: Ligue 1 (France)

### Bước 8: Khởi động Backend Server
```bash
# Vẫn trong thư mục backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend chạy tại:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs (Swagger UI)
- ReDoc: http://localhost:8000/redoc

### Bước 9 (Tùy chọn): Train ML Model
```bash
# Cài thêm ML dependencies
pip install -r requirements-ml.txt

# Train model (cần ít nhất 100 trận đã finished)
python -m app.ml.train
```

Model sẽ được lưu vào `models/prediction_model.pkl`

---

## 📱 PHẦN 2: MOBILE APP (React Native)

### Bước 1: Cài đặt Dependencies
```bash
# Mở PowerShell mới, cd vào thư mục gốc
cd d:\HK7\DACN2\ScoreFlow

# Cài đặt packages
npm install

# Hoặc nếu dùng yarn
yarn install
```

### Bước 2: Cấu hình API URL
```bash
# Tạo file .env trong thư mục gốc
# Copy từ .env.example hoặc tạo mới:

# Nếu chạy trên máy thật qua WiFi:
API_URL=http://192.168.1.100:8000

# Nếu chạy trên emulator:
API_URL=http://10.0.2.2:8000

# Thay 192.168.1.100 bằng IP máy của bạn
# Xem IP: ipconfig (Windows) / ifconfig (Mac/Linux)
```

### Bước 3: Update API URL trong code
Mở file `src/services/ApiClient.ts` và sửa:
```typescript
const API_URL = 'http://192.168.1.100:8000'; // Thay bằng IP máy bạn
```

### Bước 4: Khởi động Expo
```bash
# Khởi động development server
npx expo start

# Hoặc
npm start
```

### Bước 5: Chạy trên thiết bị

#### Option A: Điện thoại thật (Khuyến nghị)
1. Cài **Expo Go** app:
   - Android: https://play.google.com/store/apps/details?id=host.exp.exponent
   - iOS: https://apps.apple.com/app/expo-go/id982107779

2. Đảm bảo điện thoại và máy tính **cùng mạng WiFi**

3. Mở Expo Go → Scan QR code trên terminal

#### Option B: Android Emulator
```bash
# Cài Android Studio trước
# Tạo AVD (Android Virtual Device)
# Sau đó:
npx expo start --android

# Hoặc press 'a' trong terminal
```

#### Option C: iOS Simulator (chỉ macOS)
```bash
npx expo start --ios

# Hoặc press 'i' trong terminal
```

---

## ✅ Kiểm tra dự án đã chạy thành công

### Backend:
1. Truy cập http://localhost:8000/docs
2. Thử endpoint: `GET /api/v1/matches/upcoming`
3. Sẽ thấy danh sách trận đấu từ database

### Mobile:
1. App mở lên hiển thị HomeScreen
2. Thấy danh sách trận đấu (nếu đã seed data)
3. Click vào trận → xem chi tiết
4. Tab "Predictions" → xem dự đoán AI

---

## 🔧 Các lệnh hữu ích

### Backend:
```bash
# Xem logs Docker
docker-compose logs -f

# Dừng services
docker-compose down

# Xóa database và bắt đầu lại
docker-compose down -v
docker-compose up -d postgres redis

# Sync thêm matches
python -m app.cli sync-matches 2021 14

# Update live scores
python -m app.cli update-live
```

### Mobile:
```bash
# Clear cache
npx expo start -c

# Type check
npm run type-check

# Lint
npm run lint

# Build APK (cần EAS account)
npx expo install eas-cli
eas build --platform android
```

---

## ❌ Troubleshooting

### Backend không kết nối database:
```bash
# Kiểm tra PostgreSQL đang chạy
docker ps

# Xem logs
docker logs scoreflow_db

# Restart
docker-compose restart postgres
```

### Mobile không connect backend:
1. Kiểm tra firewall đã cho phép port 8000
2. Ping từ điện thoại: http://192.168.1.100:8000/docs
3. Thử đổi sang IP khác hoặc dùng ngrok:
```bash
# Cài ngrok
choco install ngrok

# Tunnel backend
ngrok http 8000

# Copy HTTPS URL vào ApiClient.ts
```

### Lỗi "API rate limit exceeded":
- Free tier Football-Data.org chỉ 10 req/min
- Đợi 1 phút rồi thử lại
- Hoặc nâng cấp lên paid plan

### Expo Go không quét được QR:
```bash
# Khởi động với tunnel mode
npx expo start --tunnel
```

---

## 📚 Tài liệu thêm

- [Expo Docs](https://docs.expo.dev/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Football-Data.org API](https://www.football-data.org/documentation/quickstart)
- [React Navigation](https://reactnavigation.org/)
- [Redux Toolkit](https://redux-toolkit.js.org/)

---

## 🎓 Workflow phát triển

### Thêm feature mới:
1. Backend: Tạo endpoint trong `backend/app/api/v1/endpoints/`
2. Mobile: Gọi API từ `src/services/`
3. Update Redux store nếu cần global state
4. Tạo/sửa screen trong `src/screens/`

### Deploy lên production:
- Backend: Docker image → Deploy lên Railway/Render/AWS
- Mobile: `eas build` → Submit lên Play Store/App Store

---

**Chúc bạn code vui vẻ! 🎉**
