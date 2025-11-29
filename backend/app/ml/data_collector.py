import pandas as pd
import requests
import io
import time
import os

# --- CẤU HÌNH ---

# 1. Các mùa giải cần lấy (Format của web này: 2324 nghĩa là 2023-2024)
# Lấy 5 mùa gần nhất để data vừa đủ tươi
SEASONS = ['2021', '2122', '2223', '2324', '2425']

# 2. Mapping Mã giải -> Tên giải (Theo đúng DB của bác)
LEAGUES_MAPPING = {
    'E0': 'Premier League',       # Anh
    'E1': 'Championship',         # Hạng nhất Anh
    'SP1': 'Primera Division',    # Tây Ban Nha (La Liga)
    'D1': 'Bundesliga',           # Đức
    'I1': 'Serie A',              # Ý
    'F1': 'Ligue 1',              # Pháp
    'N1': 'Eredivisie',           # Hà Lan
    'P1': 'Primeira Liga',        # Bồ Đào Nha
}

BASE_URL = "https://www.football-data.co.uk/mmz4281/{}/{}.csv"
OUTPUT_FILE = "training_data_europe.csv"

def download_data():
    all_data = []
    print(f"🚀 Bắt đầu tải dữ liệu của {len(LEAGUES_MAPPING)} giải đấu qua {len(SEASONS)} mùa...")

    for season in SEASONS:
        for code, league_name in LEAGUES_MAPPING.items():
            url = BASE_URL.format(season, code)
            
            try:
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    # Đọc nội dung CSV
                    csv_content = response.content.decode('utf-8', errors='ignore')
                    
                    # Bỏ qua các dòng trống hoặc lỗi format
                    if not csv_content.strip():
                        continue

                    df = pd.read_csv(io.StringIO(csv_content))
                    
                    # --- XỬ LÝ SƠ BỘ ---
                    
                    # 1. Thêm cột định danh (Để biết trận này thuộc giải nào, mùa nào)
                    df['League_Name'] = league_name
                    df['Season_Id'] = season
                    
                    # 2. Chọn lọc cột quan trọng (Giảm dung lượng, lấy Odds Bet365)
                    # Date: Ngày, HomeTeam/AwayTeam: Tên đội
                    # FTHG/FTAG: Bàn thắng Fulltime
                    # FTR: Kết quả (H/D/A) -> TARGET để train
                    # B365H/D/A: Tỷ lệ cược -> FEATURE QUAN TRỌNG
                    
                    target_cols = [
                        'Date', 'HomeTeam', 'AwayTeam', 
                        'FTHG', 'FTAG', 'FTR', 
                        'B365H', 'B365D', 'B365A', 
                        'League_Name', 'Season_Id'
                    ]
                    
                    # Chỉ giữ lại các cột tồn tại trong file (đề phòng file cũ thiếu cột)
                    existing_cols = [c for c in target_cols if c in df.columns]
                    df_clean = df[existing_cols]
                    
                    # Chỉ lấy các dòng có đủ Odds (Tránh data rác)
                    if 'B365H' in df_clean.columns:
                        df_clean = df_clean.dropna(subset=['B365H'])
                    
                    all_data.append(df_clean)
                    print(f"✅ [OK] {league_name} - Mùa {season} ({len(df_clean)} trận)")
                    
                else:
                    print(f"❌ [404] Không tìm thấy data: {league_name} - Mùa {season}")
            
            except Exception as e:
                print(f"⚠️ Lỗi tải {league_name}/{season}: {e}")
            
            # Ngủ 0.5s để server không chặn IP
            time.sleep(0.5)

    # --- TỔNG HỢP ---
    if all_data:
        print("\nĐang gộp dữ liệu...")
        master_df = pd.concat(all_data, ignore_index=True)
        
        # Chuyển đổi định dạng ngày tháng về chuẩn YYYY-MM-DD
        master_df['Date'] = pd.to_datetime(master_df['Date'], dayfirst=True, errors='coerce')
        
        # Lưu file
        save_path = os.path.join(os.getcwd(), OUTPUT_FILE)
        master_df.to_csv(save_path, index=False)
        
        print(f"\n🎉 XONG! Đã lưu file tại: {save_path}")
        print(f"📊 Tổng số trận đấu: {len(master_df)}")
        print(f"👀 5 dòng đầu tiên:\n{master_df.head()}")
    else:
        print("\nKhông lấy được dữ liệu nào cả.")

if __name__ == "__main__":
    download_data()