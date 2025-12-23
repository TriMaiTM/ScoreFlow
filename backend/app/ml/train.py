import os
from dotenv import load_dotenv

# Load env before imports
load_dotenv("backend/.env")
if not os.getenv("DATABASE_URL"):
    load_dotenv(r"d:\HK7\DACN2\ScoreFlow\backend\.env")

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
# from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import asyncio
from pathlib import Path

from app.db.database import AsyncSessionLocal
from app.db.models import Match, Team, TeamStats
from app.ml.feature_engineering import FeatureEngineer


class ModelTrainer:
    """Train match prediction model"""
    
    def __init__(self, model_type: str = "xgboost"):
        self.model_type = model_type
        self.model = None
        
    async def prepare_training_data(self, min_date: str = None):
        """Prepare training data from database"""
        print("📊 Preparing training data...")
        
        async with AsyncSessionLocal() as db:
            # Get finished matches
            query = select(Match).where(Match.status == "finished")
            
            if min_date:
                query = query.where(Match.match_date >= min_date)
            
            query = query.options(
                selectinload(Match.home_team),
                selectinload(Match.away_team)
            )
            
            result = await db.execute(query)
            matches = result.scalars().all()
            
            print(f"Found {len(matches)} finished matches")
            
            # Extract features for each match
            feature_engineer = FeatureEngineer(db)
            
            X = []
            y = []
            
            for i, match in enumerate(matches):
                if i % 100 == 0:
                    print(f"Processing {i}/{len(matches)}")
                
                try:
                    # Extract features
                    features = await feature_engineer.extract_features(match.id)
                    features_array = feature_engineer.features_to_array(features)
                    
                    # Determine outcome
                    if match.home_score > match.away_score:
                        outcome = 0  # Home win
                    elif match.home_score == match.away_score:
                        outcome = 1  # Draw
                    else:
                        outcome = 2  # Away win
                    
                    X.append(features_array[0])
                    y.append(outcome)
                    
                except Exception as e:
                    print(f"Error processing match {match.id}: {e}")
                    continue
            
            print(f"✅ Prepared {len(X)} samples")
            
            return np.array(X), np.array(y)
    
    def train(self, X_train, y_train):
        """Train model"""
        print(f"🤖 Training {self.model_type} model...")
        
        if self.model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=20,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == "xgboost":
            self.model = XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == "lightgbm":
            self.model = LGBMClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        self.model.fit(X_train, y_train)
        print("✅ Training complete")
    
    def evaluate(self, X_test, y_test):
        """Evaluate model"""
        print("📈 Evaluating model...")
        
        y_pred = self.model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\nAccuracy: {accuracy:.4f}")
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=["Home Win", "Draw", "Away Win"]))
        
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        return accuracy
    
    def save_model(self, output_path: str):
        """Save trained model"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, output_path)
        print(f"✅ Model saved to {output_path}")


async def main():
    """Main training pipeline"""
    print("🚀 Starting model training pipeline\n")
    
    # Prepare data
    trainer = ModelTrainer(model_type="xgboost")
    
    # Get data from last 2 years
    min_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
    X, y = await trainer.prepare_training_data(min_date=min_date)
    
    if len(X) < 100:
        print("⚠️  Not enough training data. Need at least 100 samples.")
        print("   Run: python -m app.cli seed")
        return
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print(f"Class distribution: Home={sum(y==0)}, Draw={sum(y==1)}, Away={sum(y==2)}\n")
    
    # Train model
    trainer.train(X_train, y_train)
    
    # Evaluate
    accuracy = trainer.evaluate(X_test, y_test)
    
    # Save model
    trainer.save_model("models/prediction_model.pkl")
    
    print(f"\n✅ Training complete! Accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
