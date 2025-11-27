from fastapi import APIRouter

from app.api.v1.endpoints import auth, matches, leagues, teams, predictions, enhanced

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(matches.router, prefix="/matches", tags=["matches"])
router.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
router.include_router(teams.router, prefix="/teams", tags=["teams"])
router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
router.include_router(enhanced.router, prefix="/enhanced", tags=["enhanced"])
