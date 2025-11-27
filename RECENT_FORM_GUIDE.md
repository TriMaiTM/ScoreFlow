# Recent Form Feature - Complete Guide

## 📊 Tổng quan

Feature **Recent Form** hiển thị 5 trận đấu gần nhất của mỗi đội bóng, bao gồm:
- Đối thủ
- Kết quả (W/D/L với màu xanh/cam/đỏ)
- Tỷ số
- Average Goals & Average Goals Conceded

---

## 🎯 Đã hoàn thành

### Backend ✅

1. **Endpoint mới**: `GET /api/v1/teams/{team_id}/recent-matches?limit=5`
   - Trả về 5 trận FINISHED gần nhất
   - Thông tin đối thủ đầy đủ (id, name, shortName, logo)
   - Kết quả W/D/L được tính sẵn
   - Sắp xếp theo ngày mới nhất

2. **Data Sync Service**:
   - Method `sync_past_matches()` để seed matches trong quá khứ
   - Chỉ lấy FINISHED matches, bỏ qua SCHEDULED
   - Support nhiều leagues: Premier League, La Liga, etc.

3. **CLI Commands**:
   ```bash
   # Seed past matches
   python -m app.cli seed-past-matches 2021 30  # 30 ngày quá khứ
   ```

### Frontend ✅

1. **UI Components**:
   - Recent Form Card luôn hiển thị
   - 2 sections: Home team & Away team
   - Match cards với opponent, score, W/D/L badge
   - Average goals calculation
   - Empty state: "Chưa có dữ liệu trận đấu gần đây"

2. **API Integration**:
   - 2 useQuery hooks: `homeRecentMatches`, `awayRecentMatches`
   - Auto-refetch khi matchId thay đổi
   - Loading & error states

3. **Styling**:
   - 40+ custom styles
   - W/D/L badges: Green (#4CAF50), Orange (#FFA726), Red (#EF5350)
   - Responsive layout
   - Match cards với shadow & border radius

---

## 🚀 Auto-Update System

### Background Scheduler

Backend có **APScheduler** chạy tự động để update dữ liệu liên tục:

| Job | Frequency | Mô tả |
|-----|-----------|-------|
| **Update Live Matches** | 2 phút | Cập nhật tỷ số trận đang diễn ra |
| **Sync Today's Matches** | 1 giờ | Lấy tất cả trận trong ngày |
| **Sync Standings** | 2 lần/ngày (6h sáng & tối) | Cập nhật bảng xếp hạng |
| **Sync Upcoming Matches** | 6 giờ | Lấy trận 7 ngày tới |

### Cách bật/tắt

File `.env`:
```env
# Bật auto-update (recommended for production)
ENABLE_SCHEDULER=true

# Tắt auto-update (chỉ dùng manual CLI)
ENABLE_SCHEDULER=false
```

---

## 📝 Hướng dẫn sử dụng

### 1. Setup lần đầu

```bash
# Bước 1: Cài dependencies
cd backend
pip install -r requirements.txt

# Bước 2: Seed past matches cho Recent Form
python -m app.cli seed-past-matches 2021 60  # Premier League 60 ngày
python -m app.cli seed-past-matches 2014 60  # La Liga 60 ngày
python -m app.cli seed-past-matches 2002 60  # Bundesliga 60 ngày

# Bước 3: Enable scheduler trong .env
echo "ENABLE_SCHEDULER=true" >> .env

# Bước 4: Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Testing

```bash
# Test endpoint trực tiếp
curl "http://localhost:8000/api/v1/teams/20/recent-matches?limit=5"

# Response mẫu:
{
  "success": true,
  "data": [
    {
      "matchId": 137,
      "date": "2025-11-23T16:30:00",
      "isHome": true,
      "opponent": {
        "id": 9,
        "name": "Tottenham Hotspur FC",
        "shortName": "Tottenham",
        "logo": "https://..."
      },
      "teamScore": 4,
      "opponentScore": 1,
      "result": "W"
    },
    ...
  ]
}
```

### 3. Seed thêm data khi cần

```bash
# Seed thêm 90 ngày cho testing
python -m app.cli seed-past-matches 2021 90

# Update manual khi cần
python -m app.cli update-live
```

---

## 🔧 Troubleshooting

### Recent Form không hiển thị?

**Nguyên nhân**: Không có FINISHED matches trong database

**Giải pháp**:
```bash
# Seed past matches
python -m app.cli seed-past-matches 2021 30

# Kiểm tra có data
curl "http://localhost:8000/api/v1/matches/finished?page=1&limit=5"
```

### Scheduler không chạy?

**Kiểm tra**:
```bash
# Check .env
cat .env | grep ENABLE_SCHEDULER

# Nếu = false, đổi thành true
ENABLE_SCHEDULER=true
```

**Restart backend** để scheduler khởi động:
```bash
uvicorn main:app --reload
# Phải thấy log: "📅 Scheduler started successfully"
```

### API rate limit exceeded?

**Nguyên nhân**: Vượt 10 requests/minute của Football-Data.org

**Giải pháp**:
1. Giảm frequency trong `scheduler.py`:
   ```python
   # Thay vì 2 phút, đổi thành 5 phút
   trigger=IntervalTrigger(minutes=5)
   ```

2. Hoặc tạm tắt scheduler:
   ```env
   ENABLE_SCHEDULER=false
   ```

### Frontend shows "Chưa có dữ liệu"?

**Debug steps**:
```bash
# 1. Check backend có data
curl "http://localhost:8000/api/v1/teams/20/recent-matches?limit=5"

# 2. Check network tab trong browser
# - Status 200?
# - Response có data array?

# 3. Check console logs
# - Có errors?
# - useQuery hook đang fetching?
```

---

## 🎨 UI Customization

### Thay đổi màu W/D/L badges

File `MatchDetailScreen.tsx`:
```typescript
resultWin: {
  backgroundColor: '#4CAF50',  // Green - thay màu khác ở đây
},
resultDraw: {
  backgroundColor: '#FFA726',  // Orange
},
resultLose: {
  backgroundColor: '#EF5350',  // Red
},
```

### Thay đổi số trận hiển thị

Backend endpoint:
```bash
# Thay vì 5, lấy 10 trận
curl "http://localhost:8000/api/v1/teams/20/recent-matches?limit=10"
```

Frontend hook:
```typescript
const { data: homeRecentData } = useQuery({
  queryKey: ['teamRecentMatches', homeTeamId],
  queryFn: () => TeamService.getTeamRecentMatches(homeTeamId, 10), // Đổi 5 thành 10
});
```

### Thêm thông tin khác

Backend có thể thêm:
- `venue`: Sân vận động
- `round`: Vòng đấu
- `matchday`: Ngày thi đấu

Frontend có thể hiển thị thêm:
- Possession %
- Shots on target
- Corners
- Cards

---

## 📊 League IDs Reference

Dùng cho `seed-past-matches`:

| League | ID | Country |
|--------|-----|---------|
| Premier League | 2021 | England |
| La Liga | 2014 | Spain |
| Bundesliga | 2002 | Germany |
| Serie A | 2019 | Italy |
| Ligue 1 | 2015 | France |
| UEFA Champions League | 2001 | Europe |
| World Cup | 2000 | International |

---

## 🔄 Workflow hoàn chỉnh

### Development Mode:
1. Tắt scheduler: `ENABLE_SCHEDULER=false`
2. Seed data thủ công khi cần test
3. Focus vào debugging & features

### Testing Mode:
1. Bật scheduler: `ENABLE_SCHEDULER=true`
2. Monitor logs để ensure jobs chạy
3. Test với real-time data

### Production Mode:
1. **Luôn bật scheduler**
2. Seed initial data trước deploy
3. Set up monitoring & alerts
4. Backup database định kỳ

---

## 📚 Documentation Files

- `DATA_SEEDING.md` - Chi tiết về seeding & scheduler
- `RECENT_FORM_GUIDE.md` - Guide này, tổng quan feature
- `backend/app/core/scheduler.py` - Scheduler implementation
- `backend/app/cli.py` - CLI commands
- `src/screens/MatchDetailScreen.tsx` - Frontend UI

---

## ✅ Checklist triển khai

- [x] Backend endpoint `/teams/{id}/recent-matches`
- [x] Frontend UI với W/D/L badges
- [x] Empty state handling
- [x] CLI command `seed-past-matches`
- [x] Background scheduler implementation
- [x] Auto-update jobs (live, standings, matches)
- [x] Documentation hoàn chỉnh
- [ ] **Testing với real users**
- [ ] **Production deployment**
- [ ] **Monitoring setup**

---

## 🎯 Next Steps

1. **Testing**: Test với nhiều teams khác nhau
2. **Optimization**: Cache recent matches để giảm API calls
3. **Analytics**: Track xem users có dùng feature này không
4. **Enhancements**: 
   - Add filters (home/away only)
   - Add date range picker
   - Show more stats (possession, shots, etc.)

---

## 💡 Tips

- Seed ít nhất **60 ngày** past matches để có đủ data cho testing
- Bật scheduler trong production để data luôn fresh
- Monitor API rate limits để avoid 429 errors
- Backup database trước khi seed large dataset
- Check logs thường xuyên để ensure scheduler chạy đúng

🎉 **Feature hoàn thành và sẵn sàng sử dụng!**
