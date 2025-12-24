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
            # Classes are likely [0, 1, 2] -> [Away, Draw, Home] based on training script
            proba = self.model.predict_proba(features)[0]
            
            # CORRECT MAPPING:
            away_prob = float(proba[0]) # Class 0
            draw_prob = float(proba[1]) # Class 1
            home_prob = float(proba[2]) # Class 2
            
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
        # Feature order (12 features): home_elo, away_elo, elo_diff, home_form, away_form, 
        # home_goals_avg, away_goals_avg, home_conceded, away_conceded, home_rest, away_rest, elo_diff_abs
        
        home_goals_avg = features[0, 5]  # Index 5
        away_goals_avg = features[0, 6]  # Index 6
        
        # Adjust based on form and Elo
        home_form = features[0, 3]  # Index 3
        away_form = features[0, 4]  # Index 4
        elo_diff = features[0, 2]
        
        # Form difference
        form_diff = home_form - away_form
        
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
        """Generate a natural language explanation for the prediction (Vietnamese)"""
        # Feature order: 
        # 0:HomeElo, 1:AwayElo, 2:EloDiff, 3:HomeForm, 4:AwayForm, 
        # 5:HomeGS, 6:AwayGS, 7:HomeGC, 8:AwayGC, 9:HomeRest, 10:AwayRest, 11:EloDiffAbs
        
        elo_diff = features[2]
        home_form = features[3]
        away_form = features[4]
        home_gs = features[5]
        away_gs = features[6]
        home_gc = features[7]
        away_gc = features[8]
        
        explanation = []
        
        # 1. Main Verdict based on Probability
        if home_prob > 0.65:
            explanation.append(f"**{home_team}** đang là ứng cử viên sáng giá cho chiến thắng.")
        elif home_prob > 0.50:
            explanation.append(f"**{home_team}** có lợi thế rất lớn, đặc biệt là khi được thi đấu trên sân nhà.")
        elif away_prob > 0.65:
            explanation.append(f"**{away_team}** được đánh giá rất cao cho chiến thắng dù phải làm khách.")
        elif away_prob > 0.50:
            explanation.append(f"**{away_team}** có phần nhỉnh hơn trong cặp đấu này.")
        else:
            explanation.append("Đây là một trận đấu rất cân bằng và khó đoán.")
            if abs(home_prob - away_prob) < 0.05:
                explanation.append("Khả năng hòa là rất cao.")

        # 2. Form & Elo Context
        if elo_diff > 100:
            if home_form > away_form:
                explanation.append(f"Với đẳng cấp vượt trội và phong độ tốt hơn, rất khó để đánh bại {home_team} lúc này.")
            elif home_form < away_form:
                explanation.append(f"Dù {home_team} được đánh giá cao hơn trên lý thuyết, nhưng phong độ tốt của {away_team} có thể tạo nên bất ngờ.")
        elif elo_diff < -100:
            if away_form > home_form:
                explanation.append(f"{away_team} sở hữu đội hình mạnh hơn và đang có đà hưng phấn.")
            elif away_form < home_form:
                explanation.append(f"{home_team} bị đánh giá thấp hơn nhưng những màn trình diễn gần đây cho thấy họ hoàn toàn có cơ hội.")
        else:
            # Close Elo
            if home_form > away_form + 0.5:
                explanation.append(f"{home_team} bước vào trận đấu với phong độ tốt hơn hẳn đối thủ.")
            elif away_form > home_form + 0.5:
                explanation.append(f"{away_team} đến làm khách với phong độ vượt trội so với đội chủ nhà.")

        # 3. Tactical / Stats Insight
        avg_goals = (home_gs + away_gs) / 2
        avg_conceded = (home_gc + away_gc) / 2
        
        if avg_goals > 1.8:
            explanation.append("Hứa hẹn sẽ có nhiều bàn thắng, khi cả hai đội đều có hàng công mạnh.")
        elif avg_conceded < 0.8:
            explanation.append("Đây có thể là một trận đấu chặt chẽ, nặng về chiến thuật và ít bàn thắng.")
        elif home_gs > 2.0 and away_gc > 1.5:
            explanation.append(f"Hàng công của {home_team} sẽ có nhiều cơ hội trước hàng thủ lỏng lẻo của {away_team}.")
            
        return " ".join(explanation)


# Global model instance
prediction_model = PredictionModel()
