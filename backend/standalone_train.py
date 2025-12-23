
import asyncio
import os
import sys
import numpy as np
import pandas as pd
import joblib
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import sys

# Setup path to import app modules
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Load Env
load_dotenv("backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    load_dotenv(r"d:\HK7\DACN2\ScoreFlow\backend\.env")
    DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Imports
from app.db.models import Match, Team, TeamStats
from app.ml.feature_engineering import FeatureEngineer

# Windows Asyncio Fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def train_model():
    print("🚀 Starting Standalone Training...")
    if not DATABASE_URL:
        print("❌ Error: No DATABASE_URL")
        return

    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        print("📊 Fetching finished matches...")
        stmt = select(Match).where(Match.status == "finished").options(
            selectinload(Match.home_team),
            selectinload(Match.away_team)
        )
        result = await db.execute(stmt)
        matches = result.scalars().all()
        print(f"✅ Found {len(matches)} matches.")

        feature_engineer = FeatureEngineer(db)
        X = []
        y = []

        print("🔄 Extracting features (this may take a while)...")
        count = 0
        for match in matches:
            try:
                features = await feature_engineer.extract_features(match.id)
                # Convert to array
                # feature_engineering.py features_to_array return shape (1, 12)
                f_array = feature_engineer.features_to_array(features)[0]
                
                # Determine Label
                if match.home_score > match.away_score:
                    label = 2 # Home
                elif match.home_score == match.away_score:
                    label = 1 # Draw
                else:
                    label = 0 # Away
                
                X.append(f_array)
                y.append(label)
                
                count += 1
                if count % 100 == 0:
                    print(f"   Processed {count}/{len(matches)}")
            except Exception as e:
                print(f"   ⚠️ Error match {match.id}: {e}")

        X = np.array(X)
        y = np.array(y)
        print(f"✅ Data Prepared: X={X.shape}, y={y.shape}")

        if len(X) < 10:
             print("❌ Not enough data to train.")
             return

        # Train
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print("🤖 Training XGBoost...")
        model = XGBClassifier(
            n_estimators=200, debug=False,
            objective='multi:softprob', num_class=3
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"🏆 Accuracy: {acc:.4f}")
        print(classification_report(y_test, preds))
        
        # Save
        # Make sure directory exists
        os.makedirs("backend/models", exist_ok=True)
        model_path = "backend/models/prediction_model.pkl"
        joblib.dump(model, model_path)
        print(f"💾 Model saved to {model_path}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(train_model())
