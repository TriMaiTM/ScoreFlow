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
    
import joblib
import numpy as np
from typing import Dict, Tuple
from pathlib import Path

from app.ml.feature_engineering import FeatureEngineer
from app.core.config import settings
from app.db.models import Match


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
    
    async def predict_match(self, match: Match, feature_engineer: FeatureEngineer) -> Dict:
        """Generate full prediction for a match"""
        # Extract features
        features_dict = await feature_engineer.extract_features(match.id)
        features_array = feature_engineer.features_to_array(features_dict)
        features_list = features_array.tolist()[0] # Convert to list for explanation
        
        # 3. Predict
        outcome = self.predict_outcome(features_array)
        predicted_home, predicted_away = self.predict_score(features_array)
        
        # 4. Generate Explanation
        explanation = self.generate_explanation(
            home_team=match.home_team.name,
            away_team=match.away_team.name,
            home_prob=outcome["home_win_probability"],
            away_prob=outcome["away_win_probability"],
            features=features_list
        )
        
        # Return result
        return {
            "matchId": match.id,
            "homeWinProbability": outcome["home_win_probability"],
            "drawProbability": outcome["draw_probability"],
            "awayWinProbability": outcome["away_win_probability"],
            "predictedScore": {
                "home": predicted_home,
                "away": predicted_away
            },
            "confidence": outcome["confidence"],
            "explanation": explanation,
            "features": {
                "home_elo": features_dict.get("home_elo"),
                "away_elo": features_dict.get("away_elo"),
                "home_form": features_dict.get("home_form_pts"),
                "away_form": features_dict.get("away_form_pts"),
                "home_rest": features_dict.get("home_rest_days"),
                "away_rest": features_dict.get("away_rest_days")
            }
        }

    def generate_explanation(self, home_team: str, away_team: str, home_prob: float, away_prob: float, features: list) -> str:
        """Generate a natural language explanation for the prediction"""
        # Features: [HomeElo, AwayElo, EloDiff, HomeFormPts, AwayFormPts, HomeGS, AwayGS, HomeGC, AwayGC, HomeRest, AwayRest, ...]
        
        elo_diff = features[2]
        home_form = features[3]
        away_form = features[4]
        
        explanation = []
        
        # 1. Analyze Probability
        if home_prob > 0.55:
            explanation.append(f"{home_team} is strongly favored to win.")
        elif home_prob > 0.40:
            explanation.append(f"{home_team} has a slight advantage.")
        elif away_prob > 0.55:
            explanation.append(f"{away_team} is strongly favored to win.")
        elif away_prob > 0.40:
            explanation.append(f"{away_team} has a slight advantage.")
        else:
            explanation.append("This match is too close to call, a draw is very likely.")
            
        # 2. Analyze Elo
        if abs(elo_diff) > 100:
            stronger = home_team if elo_diff > 0 else away_team
            explanation.append(f"{stronger} has a significantly higher Elo rating.")
        
        # 3. Analyze Form
        if home_form > 2.0 and home_form > away_form + 0.5:
            explanation.append(f"{home_team} is in excellent form recently.")
        elif away_form > 2.0 and away_form > home_form + 0.5:
            explanation.append(f"{away_team} has been playing very well lately.")
        elif home_form < 0.5 and away_form > 1.0:
            explanation.append(f"{home_team} has been struggling with poor form.")
            
        return " ".join(explanation)


# Global model instance
prediction_model = PredictionModel()
