# Hướng Dẫn Build File APK (Android)

Để xuất ra file `.apk` cài đặt trực tiếp lên điện thoại Android, chúng ta sử dụng **EAS Build** của Expo.

## Bước 1: Cài đặt EAS CLI
Nếu chưa cài, hãy chạy lệnh sau trong terminal:
```bash
npm install -g eas-cli
```

## Bước 2: Đăng nhập Expo
Bạn cần có tài khoản Expo (đăng ký tại [expo.dev](https://expo.dev/signup)).
Sau đó đăng nhập trong terminal:
```bash
eas login
```

## Bước 3: Cấu hình Project (Chỉ làm lần đầu)
Chạy lệnh sau để liên kết project với tài khoản Expo của bạn:
```bash
eas build:configure
```
- Chọn nền tảng: `All` hoặc `Android`.

## Bước 4: Build APK
Chạy lệnh sau để bắt đầu build bản **Preview** (xuất ra file APK):
```bash
eas build -p android --profile preview
```

## Bước 5: Tải file APK
- Quá trình build sẽ diễn ra trên Cloud của Expo (mất khoảng 10-20 phút tùy server).
- Khi xong, terminal sẽ hiện ra một đường link tải file `.apk`.
- Bạn cũng có thể vào Dashboard của Expo để tải.

## Lưu ý
- **Free Tier**: Tài khoản miễn phí có thể phải chờ (queue) nếu server đông.
- **Dung lượng**: File APK build ra sẽ khoảng 30-50MB.
