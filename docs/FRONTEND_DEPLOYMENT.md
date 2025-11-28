# Hướng Dẫn Deploy Frontend (Expo Web) lên Vercel

Hướng dẫn này sẽ giúp bạn đưa giao diện Web của ScoreFlow lên Vercel để mọi người có thể truy cập qua mạng Internet.

## Cách 1: Deploy bằng Vercel CLI (Nhanh nhất)

Cách này không cần đẩy code lên GitHub, deploy trực tiếp từ máy tính.

### Bước 1: Cài đặt Vercel CLI
Mở terminal (tại thư mục gốc `ScoreFlow`) và chạy lệnh:
```bash
npm install -g vercel
```

### Bước 2: Đăng nhập Vercel
Chạy lệnh sau và làm theo hướng dẫn (chọn Login with GitHub/Email):
```bash
vercel login
```

### Bước 3: Cấu hình Build cho Expo
Tạo file `vercel.json` ở thư mục gốc `ScoreFlow` (nếu chưa có) với nội dung sau:
```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
  "framework": "create-react-app",
  "buildCommand": "npx expo export -p web",
  "outputDirectory": "dist"
}
```

### Bước 4: Deploy
Chạy lệnh sau để deploy:
```bash
vercel --prod
```
- **Set up and deploy?**: `Y`
- **Which scope?**: (Chọn tài khoản của bạn)
- **Link to existing project?**: `N`
- **Project name**: `scoreflow-frontend` (hoặc tên tùy thích)
- **In which directory?**: `./` (Enter)
- **Want to modify these settings?**: `N` (Vì mình đã cấu hình trong `vercel.json` rồi)

Ngồi đợi khoảng 1-2 phút. Khi xong nó sẽ nhả ra cái link (ví dụ: `https://scoreflow-frontend.vercel.app`). Bấm vào là chạy!

---

## Cách 2: Deploy qua GitHub (Khuyên dùng lâu dài)

Cách này giúp tự động deploy mỗi khi bạn push code mới lên GitHub.

1.  **Push code lên GitHub**: Đảm bảo code frontend mới nhất đã ở trên GitHub.
2.  **Vào Dashboard Vercel**: [https://vercel.com/dashboard](https://vercel.com/dashboard)
3.  **Add New Project**: Chọn **Import** từ GitHub Repository của bạn.
4.  **Configure Project**:
    *   **Framework Preset**: Chọn **Other** (hoặc Create React App).
    *   **Build Command**: `npx expo export -p web`
    *   **Output Directory**: `dist`
5.  **Environment Variables**: (Nếu cần, ví dụ API Key, nhưng App này đang hardcode API URL trong code nên không cần).
6.  **Deploy**: Bấm nút Deploy và đợi.

## Lưu ý quan trọng
- **API URL**: Đảm bảo file `src/services/ApiClient.ts` đã trỏ về Backend trên Render (`https://scoreflow-backend-5wu8.onrender.com/api/v1`).
- **Web Compatibility**: Đảm bảo code không dùng các thư viện chỉ dành cho Mobile (như `SecureStore` mà mình vừa fix).
