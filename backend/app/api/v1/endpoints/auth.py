from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import User
from app.schemas.schemas import UserCreate, Token, ApiResponse
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
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
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
async def login(email: str, password: str, db: AsyncSession = Depends(get_db)):
    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return ApiResponse(
        success=True,
        data={
            "token": access_token,
            "userId": str(user.id),
            "email": user.email,
        },
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    return ApiResponse(success=True, message="Logged out successfully")


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return ApiResponse(success=True, data=current_user)
