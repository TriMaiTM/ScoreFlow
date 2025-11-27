from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.schemas import ApiResponse
from app.ml.model import prediction_model
from app.ml.feature_engineering import FeatureEngineer

router = APIRouter()


@router.get("/{match_id}", response_model=ApiResponse)
async def get_prediction(match_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Create feature engineer
        feature_engineer = FeatureEngineer(db)
        
        # Generate prediction
        prediction = await prediction_model.predict_match(match_id, feature_engineer)
        
        return ApiResponse(success=True, data=prediction)
    except Exception as e:
        return ApiResponse(success=False, message=str(e))
