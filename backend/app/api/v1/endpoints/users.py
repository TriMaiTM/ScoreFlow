
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import shutil
import os
from pathlib import Path

from app.db.database import get_db
from app.db.models import User
from app.core.security import get_current_user
from app.schemas.schemas import ApiResponse

router = APIRouter()

# Setup static/avatars directory
UPLOAD_DIR = Path("static/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/me/avatar", response_model=ApiResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user["user_id"]
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    
    # Generate filename
    extension = file.filename.split(".")[-1]
    filename = f"{user_id}_avatar.{extension}"
    file_path = UPLOAD_DIR / filename
    
    # Save file
    try:
        print(f"📂 Saving avatar for user {user_id}: {file.filename}")
        print(f"   Target path: {file_path}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print("✅ File saved successfully")
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Could not save file: {e}")
        
    # Update DB
    avatar_url = f"/static/avatars/{filename}"
    
    # We need to fetch the user object to update it
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user:
        user.avatar_url = avatar_url
        await db.commit()
    
    return ApiResponse(
        success=True,
        message="Avatar uploaded successfully",
        data={"avatarUrl": avatar_url}
    )

@router.get("/verify")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.verification_token == token))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(400, "Invalid verification token")
        
    if user.is_verified:
        return {"message": "Email already verified"}
        
    user.is_verified = True
    user.verification_token = None # Optional: Clear token
    await db.commit()
    
    return {"message": "Email verified successfully! You can now login."}


@router.post("/me/push-token", response_model=ApiResponse)
async def update_push_token(
    token_data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save Expo Push Token for the user"""
    user_id = int(current_user["user_id"])
    push_token = token_data.get("token")
    
    if not push_token:
        raise HTTPException(400, "Token is required")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user:
        user.push_token = push_token
        await db.commit()
        
    return ApiResponse(
        success=True,
        message="Push token updated"
    )

@router.post("/me/favorites/teams/{team_id}", response_model=ApiResponse)
async def add_favorite_team(
    team_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = int(current_user["user_id"])
    
    # Check if already exists
    from app.db.models import FavoriteTeam
    result = await db.execute(
        select(FavoriteTeam).where(
            FavoriteTeam.user_id == user_id, 
            FavoriteTeam.team_id == team_id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return ApiResponse(success=True, message="Team already in favorites")
        
    new_fav = FavoriteTeam(user_id=user_id, team_id=team_id)
    db.add(new_fav)
    await db.commit()
    
    return ApiResponse(success=True, message="Team added to favorites")

@router.delete("/me/favorites/teams/{team_id}", response_model=ApiResponse)
async def remove_favorite_team(
    team_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = int(current_user["user_id"])
    
    from app.db.models import FavoriteTeam
    result = await db.execute(
        select(FavoriteTeam).where(
            FavoriteTeam.user_id == user_id, 
            FavoriteTeam.team_id == team_id
        )
    )
    fav = result.scalar_one_or_none()
    
    if fav:
        await db.delete(fav)
        await db.commit()
        
    return ApiResponse(success=True, message="Team removed from favorites")
