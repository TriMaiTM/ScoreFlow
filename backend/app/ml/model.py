import joblib
import numpy as np
from typing import Dict, Tuple
from pathlib import Path

from app.ml.feature_engineering import FeatureEngineer
from app.core.config import settings


class PredictionModel:
    """Match prediction model"""
    
    def __init__(self):
        self.model = None
        self.model_path = Path(settings.MODEL_PATH)
        self.load_model()
    
    def load_model(self):
        """Load trained model"""
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            print(f"✅ Loaded model from {self.model_path}")
        else:
            print(f"⚠️  Model not found at {self.model_path}")
            print("   Using baseline predictions")
    
    def predict_outcome(self, features: np.ndarray) -> Dict[str, float]:
        """Predict match outcome probabilities"""
        if self.model is None:
            # Baseline prediction using Elo difference
            elo_diff = features[0, 2]  # elo_diff is 3rd feature
            
            # Simple logistic function
            home_prob = 1 / (1 + np.exp(-elo_diff / 400))
            draw_prob = 0.25
            away_prob = 1 - home_prob - draw_prob
            
            # Normalize
            total = home_prob + draw_prob + away_prob
            home_prob /= total
            draw_prob /= total
            away_prob /= total
            
            confidence = 0.5  # Low confidence for baseline
        else:
            # Use trained model
            proba = self.model.predict_proba(features)[0]
            home_prob = float(proba[0])
            draw_prob = float(proba[1])
            away_prob = float(proba[2])
            
            # Confidence based on max probability
            confidence = max(home_prob, draw_prob, away_prob)
        
        return {
            "home_win_probability": home_prob,
            "draw_probability": draw_prob,
            "away_win_probability": away_prob,
            "confidence": confidence
        }
    
    def predict_score(self, features: np.ndarray) -> Tuple[int, int]:
        """Predict match score"""
        # Simple approach: use goals averages
        home_goals_avg = features[0, 6]
        away_goals_avg = features[0, 7]
        
        # Adjust based on form and Elo
        form_diff = features[0, 5]
        elo_diff = features[0, 2]
        
        home_adjustment = (form_diff + elo_diff / 1000) * 0.5
        away_adjustment = -(form_diff + elo_diff / 1000) * 0.5
        
        predicted_home = max(0, round(home_goals_avg + home_adjustment))
        predicted_away = max(0, round(away_goals_avg + away_adjustment))
        
        return int(predicted_home), int(predicted_away)
    
    async def predict_match(self, match_id: int, feature_engineer: FeatureEngineer) -> Dict:
        """Generate full prediction for a match"""
        # Extract features
        features_dict = await feature_engineer.extract_features(match_id)
        features_array = feature_engineer.features_to_array(features_dict)
        
        # Predict outcome
        outcome = self.predict_outcome(features_array)
        
        # Predict score
        predicted_home, predicted_away = self.predict_score(features_array)
        
        return {
            "matchId": match_id,
            "homeWinProbability": outcome["home_win_probability"],
            "drawProbability": outcome["draw_probability"],
            "awayWinProbability": outcome["away_win_probability"],
            "predictedScore": {
                "home": predicted_home,
                "away": predicted_away
            },
            "confidence": outcome["confidence"],
            "features": features_dict
        }


# Global model instance
prediction_model = PredictionModel()
