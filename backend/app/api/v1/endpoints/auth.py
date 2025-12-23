from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import User
from app.schemas.schemas import UserCreate, UserLogin, Token, ApiResponse
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)

router = APIRouter()


@router.post("/register", response_model=ApiResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    import uuid
    verification_token = str(uuid.uuid4())
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
        verification_token=verification_token,
        is_verified=False
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Mock Email Sending
    print(f"\n[MOCK EMAIL] Verification Link: https://scoreflow-backend-5wu8.onrender.com/api/v1/users/verify?token={verification_token}\n")
    
    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email})
    
    return ApiResponse(
        success=True,
        data={
            "token": access_token,
            "userId": str(new_user.id),
            "email": new_user.email,
        },
    )


@router.post("/login", response_model=ApiResponse)
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    # Find user
    result = await db.execute(select(User).where(User.email == user_credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    # Get favorites IDs
    from app.db.models import FavoriteTeam
    fav_teams_result = await db.execute(select(FavoriteTeam.team_id).where(FavoriteTeam.user_id == user.id))
    favorite_teams = [row[0] for row in fav_teams_result.all()]
    
    # Construct profile
    profile_data = {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "avatarUrl": user.avatar_url,
        "favoriteTeams": favorite_teams,
        "favoriteLeagues": [], # TODO: Implement Favorite Leagues
        "followedMatches": [], # TODO: Implement Followed Matches
        "notificationSettings": {
            "enabled": True,
            "matchStart": True,
            "goals": True,
            "matchEnd": True,
            "favoriteTeamsOnly": False
        }
    }
    
    return ApiResponse(
        success=True,
        data={
            "token": access_token,
            "userId": str(user.id),
            "email": user.email,
            "profile": profile_data
        },
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    return ApiResponse(success=True, message="Logged out successfully")


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = int(current_user["user_id"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(404, "User not found")
        
    # Get favorites
    from app.db.models import FavoriteTeam
    fav_teams_result = await db.execute(select(FavoriteTeam.team_id).where(FavoriteTeam.user_id == user_id))
    favorite_teams = [row[0] for row in fav_teams_result.all()]
        
    # Construct profile
    profile_data = {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "avatarUrl": user.avatar_url,
        "favoriteTeams": favorite_teams,
        "favoriteLeagues": [],
        "followedMatches": [],
        "notificationSettings": {
            "enabled": True,
            "matchStart": True,
            "goals": True,
            "matchEnd": True,
            "favoriteTeamsOnly": False
        }
    }
    
    return ApiResponse(success=True, data=profile_data)
