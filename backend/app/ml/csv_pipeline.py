import pandas as pd
import numpy as np
import json
import joblib
import asyncio
from pathlib import Path
from datetime import datetime
from sqlalchemy import select
from thefuzz import process
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from app.db.database import AsyncSessionLocal
from app.db.models import Team

# Constants
K_FACTOR_BASE = 20
ELO_START = 1500
MAPPING_FILE = Path("app/ml/team_mapping.json")
MODEL_PATH = Path("models/prediction_model_v2.pkl")
CSV_PATH = Path("app/ml/data_training.csv")

class CSVPipeline:
    def __init__(self):
        self.team_mapping = {}
        self.elo_ratings = {}  # team_id -> rating
        self.team_stats = {}   # team_id -> {matches_played, goals_scored, ...}
        self.last_match_date = {} # team_id -> last match date (datetime)

    async def load_teams_from_db(self):
        """Fetch all teams from DB for mapping"""
        print("📥 Fetching teams from database...")
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Team))
            teams = result.scalars().all()
            return teams

    async def create_team_mapping(self):
        """Map CSV team names to DB team IDs using fuzzy matching"""
        if MAPPING_FILE.exists():
            print(f"📂 Loading existing mapping from {MAPPING_FILE}")
            with open(MAPPING_FILE, "r") as f:
                self.team_mapping = json.load(f)
            return

        print("🔍 Creating new team mapping...")
        df = pd.read_csv(CSV_PATH)
        csv_teams = set(df["HomeTeam"].unique()) | set(df["AwayTeam"].unique())
        
        db_teams = await self.load_teams_from_db()
        
        # Create lookup dictionaries
        db_teams_dict = {t.name: t.id for t in db_teams}
        db_short_names = {t.short_name: t.id for t in db_teams if t.short_name}
        
        mapping = {}
        
        for csv_team in csv_teams:
            # 1. Try exact match with short_name
            if csv_team in db_short_names:
                mapping[csv_team] = db_short_names[csv_team]
                print(f"✅ Exact match (Short): {csv_team} -> ID {mapping[csv_team]}")
                continue
                
            # 2. Try exact match with full name
            if csv_team in db_teams_dict:
                mapping[csv_team] = db_teams_dict[csv_team]
                print(f"✅ Exact match (Full): {csv_team} -> ID {mapping[csv_team]}")
                continue
            
            # 3. Fuzzy match against short_names
            match_short, score_short = process.extractOne(csv_team, list(db_short_names.keys()))
            
            # 4. Fuzzy match against full names
            match_full, score_full = process.extractOne(csv_team, list(db_teams_dict.keys()))
            
            # Pick the best match
            if score_short > score_full and score_short >= 80:
                mapping[csv_team] = db_short_names[match_short]
                print(f"⚠️  Fuzzy match (Short): {csv_team} -> {match_short} ({score_short}%)")
            elif score_full >= 80:
                mapping[csv_team] = db_teams_dict[match_full]
                print(f"⚠️  Fuzzy match (Full): {csv_team} -> {match_full} ({score_full}%)")
            else:
                print(f"❌ No match found for: {csv_team}")
        
        self.team_mapping = mapping
        
        # Save mapping
        with open(MAPPING_FILE, "w") as f:
            json.dump(mapping, f, indent=2)
        print(f"💾 Mapping saved to {MAPPING_FILE}")

    def calculate_elo_change(self, home_rating, away_rating, result, home_odds, away_odds):
        """
        Calculate Elo change with Odds weighting.
        result: 1 (Home Win), 0.5 (Draw), 0 (Away Win)
        """
        # Expected score based on rating difference
        expected_home = 1 / (1 + 10 ** ((away_rating - home_rating) / 400))
        
        # Dynamic K-factor based on Odds
        # If Home wins and Home Odds were high (Underdog wins) -> Higher K
        # If Home wins and Home Odds were low (Favorite wins) -> Lower K
        
        k_multiplier = 1.0
        
        if result == 1: # Home Win
            # Higher odds = bigger upset = bigger K
            k_multiplier = max(1.0, home_odds / 2.0) 
        elif result == 0: # Away Win
            k_multiplier = max(1.0, away_odds / 2.0)
        
        k_factor = K_FACTOR_BASE * k_multiplier
        
        change = k_factor * (result - expected_home)
        return change

    def get_last_5_form(self, team_id, match_date, df):
        """Calculate form from previous matches in DataFrame"""
        # Filter matches involving this team BEFORE current date
        # Note: This is slow for large datasets, optimization would be needed for production
        # For training script, we can optimize by maintaining running stats
        return self.team_stats.get(team_id, {
            "points": 0, "goals_scored": 0, "goals_conceded": 0
        })

    def update_team_stats(self, team_id, points, gs, gc):
        if team_id not in self.team_stats:
            self.team_stats[team_id] = {"history": []}
        
        history = self.team_stats[team_id]["history"]
        history.append({"p": points, "gs": gs, "gc": gc})
        
        # Keep last 5
        if len(history) > 5:
            history.pop(0)
            
        # Calculate averages
        total_p = sum(m["p"] for m in history)
        total_gs = sum(m["gs"] for m in history)
        total_gc = sum(m["gc"] for m in history)
        
        self.team_stats[team_id].update({
            "points_avg": total_p / len(history),
            "gs_avg": total_gs / len(history),
            "gc_avg": total_gc / len(history)
        })

    def prepare_features(self):
        """Process CSV and generate features"""
        print("� Processing matches and calculating features...")
        df = pd.read_csv(CSV_PATH)
        # Handle various date formats (ISO, DD/MM/YYYY, etc.)
        df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=True)
        df = df.sort_values('Date')
        
        features = []
        labels = []
        
        # Initialize Elo and Last Match Date
        for team_id in self.team_mapping.values():
            self.elo_ratings[team_id] = ELO_START
            self.last_match_date[team_id] = None
            
        for _, row in df.iterrows():
            home_name = row['HomeTeam']
            away_name = row['AwayTeam']
            match_date = row['Date']
            
            if home_name not in self.team_mapping or away_name not in self.team_mapping:
                continue
                
            home_id = self.team_mapping[home_name]
            away_id = self.team_mapping[away_name]
            
            # Current Ratings
            home_elo = self.elo_ratings.get(home_id, ELO_START)
            away_elo = self.elo_ratings.get(away_id, ELO_START)
            
            # Current Form
            home_stats = self.team_stats.get(home_id, {"points_avg": 0, "gs_avg": 0, "gc_avg": 0})
            away_stats = self.team_stats.get(away_id, {"points_avg": 0, "gs_avg": 0, "gc_avg": 0})
            
            # Rest Days Calculation
            def get_rest_days(tid, current_date):
                last_date = self.last_match_date.get(tid)
                if last_date is None:
                    return 7 # Default to 7 days if no history
                days = (current_date - last_date).days
                return min(days, 30) # Cap at 30 days to avoid outliers
            
            home_rest = get_rest_days(home_id, match_date)
            away_rest = get_rest_days(away_id, match_date)

            # Build Feature Vector
            # [HomeElo, AwayElo, EloDiff, HomeFormPts, AwayFormPts, HomeGS, AwayGS, HomeGC, AwayGC, HomeRest, AwayRest, OddsH, OddsD, OddsA, EloDiffAbs]
            # Note: Adding Odds as features for historical context if available, but be careful about leakage if not available in future.
            # User requested "Feature Importance", so let's include Odds to see their impact, but we must handle missing odds carefully.
            # However, for the PRODUCTION model to work without future odds, we should ideally NOT include them, OR have a fallback.
            # The user said "nếu chỉ cần odd cho lịch sử cũng được thôi, không cần tương lai đâu". 
            # This implies we CAN use odds for training to understand the match better, but wait, if we train with odds, we NEED odds for inference.
            # If we don't have odds for tomorrow's match, the model will fail or perform poorly if we pass dummy values.
            # DECISION: We will INCLUDE Odds in training to see importance as requested, BUT for the deployed model, we might need to fetch odds or use a separate model without odds.
            # actually, let's stick to the plan: Odds-Weighted Elo (already done).
            # User said "dùng cả odds và phong độ lịch sử để tận dụng tối đa".
            # Let's add Odds to the feature vector for NOW to see importance, but keep in mind the inference limitation.
            
            h_odd = row.get('B365H', 0)
            d_odd = row.get('B365D', 0)
            a_odd = row.get('B365A', 0)
            if pd.isna(h_odd): h_odd = 0
            if pd.isna(d_odd): d_odd = 0
            if pd.isna(a_odd): a_odd = 0

            feature_row = [
                home_elo,
                away_elo,
                home_elo - away_elo,
                home_stats["points_avg"],
                away_stats["points_avg"],
                home_stats["gs_avg"],
                away_stats["gs_avg"],
                home_stats["gc_avg"],
                away_stats["gc_avg"],
                home_rest,
                away_rest,
                h_odd, # Adding odds to see importance
                d_odd,
                a_odd,
                abs(home_elo - away_elo)
            ]
            
            features.append(feature_row)
            
            # Determine Label
            # FTR: H=Home Win, D=Draw, A=Away Win
            # XGBoost expects 0, 1, 2.
            # Let's map: H -> 2, D -> 1, A -> 0 (just to check "reversed" comment, but standard is usually 0,1,2 arbitrary)
            # Let's stick to: Away=0, Draw=1, Home=2 to align with "Home is higher" intuition? 
            # Or Home=0, Draw=1, Away=2. 
            # The user said "Mapping Label bị ngược". Let's check previous output.
            # Previous output: Home precision 0.52, recall 0.69. Away precision 0.42.
            # If we map H->0, D->1, A->2.
            # Let's try: Home=2, Draw=1, Away=0.
            
            if row['FTR'] == 'H':
                label = 2 # Home Win
                result_val = 1
                h_pts, a_pts = 3, 0
            elif row['FTR'] == 'D':
                label = 1 # Draw
                result_val = 0.5
                h_pts, a_pts = 1, 1
            else:
                label = 0 # Away Win
                result_val = 0
                h_pts, a_pts = 0, 3
                
            labels.append(label)
            
            # Update Elo (Odds-Weighted)
            # Use B365 odds if available, else default to 2.0 (neutral)
            h_odd_elo = row.get('B365H', 2.0)
            a_odd_elo = row.get('B365A', 2.0)
            if pd.isna(h_odd_elo): h_odd_elo = 2.0
            if pd.isna(a_odd_elo): a_odd_elo = 2.0
            
            elo_change = self.calculate_elo_change(home_elo, away_elo, result_val, h_odd_elo, a_odd_elo)
            self.elo_ratings[home_id] += elo_change
            self.elo_ratings[away_id] -= elo_change
            
            # Update Form
            self.update_team_stats(home_id, h_pts, row['FTHG'], row['FTAG'])
            self.update_team_stats(away_id, a_pts, row['FTAG'], row['FTHG'])
            
            # Update Last Match Date
            self.last_match_date[home_id] = match_date
            self.last_match_date[away_id] = match_date
            
        print(f"✅ Processed {len(features)} matches")
        
        # Save final Elo ratings for inference usage
        with open("app/ml/elo_ratings.json", "w") as f:
            json.dump(self.elo_ratings, f)
            
        return np.array(features), np.array(labels)

    def train_model(self):
        """Train XGBoost model"""
        from sklearn.utils.class_weight import compute_sample_weight
        
        X, y = self.prepare_features()
        
        print(f"🤖 Data Shape: {X.shape}")
        
        # Sequential Split (No Shuffle) to prevent Time Travel
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"✂️  Train: {len(X_train)} | Test: {len(X_test)} (Sequential Split)")
        
        # Calculate sample weights to balance classes (Give more weight to Draws)
        sample_weights = compute_sample_weight(class_weight='balanced', y=y_train)
        
        model = XGBClassifier(
            n_estimators=1500,        
            learning_rate=0.01,       
            max_depth=5,              
            min_child_weight=3,       
            gamma=0.1,                
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,            
            reg_lambda=1.0,           
            random_state=42,
            objective='multi:softprob',
            num_class=3,
            eval_metric='mlogloss'
        )
        
        model.fit(X_train, y_train, sample_weight=sample_weights, eval_set=[(X_test, y_test)], verbose=100)
        
        # Evaluate
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"\n🏆 Model Accuracy: {acc:.4f}")
        # Target names must match 0, 1, 2. We mapped Away=0, Draw=1, Home=2
        print(classification_report(y_test, y_pred, target_names=['Away', 'Draw', 'Home']))
        
        # Feature Importance
        feature_names = [
            "HomeElo", "AwayElo", "EloDiff", 
            "HomeForm", "AwayForm", 
            "HomeGS", "AwayGS", "HomeGC", "AwayGC", 
            "HomeRest", "AwayRest",
            "OddsH", "OddsD", "OddsA",
            "EloDiffAbs"
        ]
        
        importance = model.feature_importances_
        fi_df = pd.DataFrame({"Feature": feature_names, "Score": importance})
        fi_df = fi_df.sort_values(by="Score", ascending=False)
        print("\n📊 FEATURE IMPORTANCE:")
        print(fi_df)
        
        # Save
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        print(f"💾 Model saved to {MODEL_PATH}")

async def main():
    pipeline = CSVPipeline()
    await pipeline.create_team_mapping()
    pipeline.train_model()

if __name__ == "__main__":
    asyncio.run(main())
