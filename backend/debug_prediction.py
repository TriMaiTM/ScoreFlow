
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from dotenv import load_dotenv

# Setup path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.models import Match, Team
from app.ml.feature_engineering import FeatureEngineer
from app.ml.model import prediction_model

# Load env
load_dotenv("backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def debug_prediction():
    if not DATABASE_URL:
        print("❌ Error: No DATABASE_URL")
        return

    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        # 1. Find the match (Benfica vs Famalicao)
        print("🔍 Searching for match: Benfica vs Famalicao...")
        
        # We search by substring case-insensitive
        stmt = select(Match).options(
            selectinload(Match.home_team),
            selectinload(Match.away_team)
        ).join(
            Match.home_team
        ).where(
            Match.home_team.name.ilike("%Benfica%")
        )
        
        result = await session.execute(stmt)
        matches = result.scalars().all()
        
        target_match = None
        for m in matches:
            if "Famalicao" in m.away_team.name or "Famalicão" in m.away_team.name:
                target_match = m
                break
        
        if not target_match:
            print("❌ Match not found in DB!")
            return

        print(f"✅ Found Match ID: {target_match.id} | {target_match.home_team.name} vs {target_match.away_team.name} | Date: {target_match.match_date}")

        # 2. Run Prediction
        print("\n🔮 Running Prediction Debug...")
        feature_engineer = FeatureEngineer(session)
        
        try:
            # Check features first (often where it fails)
            print("   👉 Calculating features...")
            features = await feature_engineer.calculate_features(target_match)
            print(f"   ✅ Features calculated: {list(features.keys())}")
            
            # Predict
            print("   👉 Predicting...")
            prediction = await prediction_model.predict_match(target_match, feature_engineer)
            print("   ✅ Prediction Success!")
            print(prediction)
            
        except Exception as e:
            print(f"\n❌ PREDICTION FAILED ERROR: {e}")
            import traceback
            traceback.print_exc()

    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_prediction())
