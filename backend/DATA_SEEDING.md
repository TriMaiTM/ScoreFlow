# Data Seeding & Auto-Update Guide

## 📋 Tổng quan

ScoreFlow có 2 cơ chế cập nhật dữ liệu:

1. **Manual Seeding** - Chạy CLI commands để seed dữ liệu theo nhu cầu
2. **Auto-Update** - Background scheduler tự động cập nhật liên tục

---

## 🌱 Manual Seeding

### 1. Seed dữ liệu ban đầu
```bash
cd backend
python -m app.cli seed
```
- Sync tất cả leagues
- Sync matches 14 ngày tới cho các giải phổ biến
- Dùng để setup lần đầu

### 2. Seed past FINISHED matches (cho Recent Form)
```bash
# Seed 30 ngày quá khứ của Premier League
python -m app.cli seed-past-matches 2021 30

# Seed 60 ngày quá khứ của La Liga
python -m app.cli seed-past-matches 2014 60

# Seed 90 ngày của Bundesliga
python -m app.cli seed-past-matches 2002 90
```

**League IDs (Football-Data.org):**
- `2021` - Premier League (England)
- `2014` - La Liga (Spain)
- `2002` - Bundesliga (Germany)
- `2019` - Serie A (Italy)
- `2015` - Ligue 1 (France)

### 3. Sync upcoming matches
```bash
# Sync 7 ngày tới
python -m app.cli sync-matches 2021 7

# Sync 14 ngày tới
python -m app.cli sync-matches 2021 14
```

### 4. Sync standings/table
```bash
python -m app.cli sync-standings 2021
```

### 5. Update live matches manually
```bash
python -m app.cli update-live
```

---

## 🤖 Auto-Update (Background Scheduler)

### Cấu hình

Trong file `.env`:
```env
ENABLE_SCHEDULER=true  # Bật auto-update
# hoặc
ENABLE_SCHEDULER=false # Tắt auto-update (chỉ dùng manual)
```

### Lịch tự động (khi ENABLE_SCHEDULER=true)

1. **Update live matches** - Mỗi 2 phút
   - Cập nhật tỷ số các trận đang diễn ra
   - Chỉ chạy khi có trận LIVE

2. **Sync today's matches** - Mỗi 1 giờ
   - Lấy tất cả trận trong ngày
   - Đảm bảo không bỏ sót trận mới

3. **Sync league standings** - 2 lần/ngày (6h sáng & 6h tối)
   - Cập nhật bảng xếp hạng
   - Tính điểm, hiệu số, thứ hạng

4. **Sync upcoming matches** - Mỗi 6 giờ
   - Lấy trận 7 ngày tới
   - Đảm bảo lịch thi đấu luôn mới

### Kiểm tra logs

```bash
# Khi start backend, sẽ thấy:
📅 Scheduler started successfully
  - Live matches: Every 2 minutes
  - Today's matches: Every hour
  - Standings: Twice daily (6 AM, 6 PM)
  - Upcoming matches: Every 6 hours
```

### Tắt/Bật Scheduler

**Tắt:**
```env
ENABLE_SCHEDULER=false
```
- Restart backend
- Không có background jobs
- Phải update thủ công bằng CLI

**Bật:**
```env
ENABLE_SCHEDULER=true
```
- Restart backend
- Tự động chạy các jobs theo lịch
- Dữ liệu luôn được cập nhật

---

## 🎯 Workflow đề xuất

### Lần đầu setup:

1. **Seed dữ liệu cơ bản:**
```bash
python -m app.cli seed
```

2. **Seed past matches cho Recent Form testing:**
```bash
# Premier League - 60 ngày quá khứ
python -m app.cli seed-past-matches 2021 60

# La Liga - 60 ngày quá khứ
python -m app.cli seed-past-matches 2014 60
```

3. **Sync standings:**
```bash
python -m app.cli sync-standings 2021
python -m app.cli sync-standings 2014
```

4. **Bật auto-update trong .env:**
```env
ENABLE_SCHEDULER=true
```

5. **Start backend:**
```bash
uvicorn main:app --reload
```

### Development:

- Tắt scheduler nếu đang test/debug:
  ```env
  ENABLE_SCHEDULER=false
  ```

- Update manual khi cần:
  ```bash
  python -m app.cli update-live
  python -m app.cli sync-matches 2021 7
  ```

### Production:

- **Luôn bật scheduler:**
  ```env
  ENABLE_SCHEDULER=true
  ```

- Dữ liệu tự động cập nhật liên tục
- Không cần chạy CLI thủ công
- Monitoring qua logs để ensure jobs chạy đúng

---

## 📊 API Rate Limits

**Football-Data.org Free Tier:**
- 10 requests/minute
- 20,000 requests/month

**Scheduler được optimize để:**
- Live matches: Chỉ chạy khi có trận LIVE
- Batch requests: Gộp nhiều leagues trong 1 lần
- Smart caching: Tránh fetch dữ liệu trùng

**Nếu vượt rate limit:**
- Tăng interval time trong `scheduler.py`
- Giảm số leagues trong `popular_leagues`
- Hoặc upgrade API plan

---

## 🐛 Troubleshooting

### Scheduler không chạy:
```bash
# Check .env
ENABLE_SCHEDULER=true

# Check logs khi start
📅 Scheduler started successfully
```

### Không có FINISHED matches:
```bash
# Seed past matches
python -m app.cli seed-past-matches 2021 30
```

### API rate limit exceeded:
```bash
# Check API response
ERROR: 429 Too Many Requests

# Solution: Đợi 1 phút hoặc giảm frequency
```

### Matches không update:
```bash
# Manual update
python -m app.cli update-live

# Check API key valid
curl -H "X-Auth-Token: YOUR_KEY" https://api.football-data.org/v4/matches
```

---

## 📝 Best Practices

1. **Seed trước khi deploy:**
   - Chạy `seed` và `seed-past-matches` locally
   - Ensure database có dữ liệu
   - Deploy với scheduler enabled

2. **Monitor logs:**
   - Check scheduler jobs run successfully
   - Watch for API errors
   - Monitor rate limits

3. **Backup database:**
   - Trước khi seed large dataset
   - Sau khi seed thành công

4. **Test mode:**
   - Disable scheduler khi test
   - Use manual commands
   - Enable lại khi production

---

## 🚀 Quick Start Commands

```bash
# 1. Cài dependencies
pip install -r requirements.txt

# 2. Seed initial data
python -m app.cli seed

# 3. Seed past matches (cho Recent Form)
python -m app.cli seed-past-matches 2021 60
python -m app.cli seed-past-matches 2014 60

# 4. Enable auto-update
echo "ENABLE_SCHEDULER=true" >> .env

# 5. Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Done! Dữ liệu sẽ tự động cập nhật liên tục. 🎉
