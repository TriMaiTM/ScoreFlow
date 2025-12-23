from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
import asyncio
import logging

from app.db.database import get_db
from app.db.models import User, Match, Team, League, Prediction
from app.core.security import get_current_user, create_access_token
from app.schemas.schemas import ApiResponse, MatchBase, UserResponse, UserCreate
from app.services.data_sync import DataSyncService

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Global Seed Status ---
SEED_STATUS = {
    "is_running": False,
    "progress": 0,
    "total": 0,
    "message": "Idle",
    "updated_at": None
}

# --- Dependencies ---

async def get_current_superuser(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Check if current user is a superuser"""
    # current_user is a dict from get_current_user containing "user_id" and "email"
    try:
        user_id = int(current_user.get("user_id"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid user ID in token")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return user


# --- Admin Auth ---

@router.post("/login", response_model=ApiResponse)
async def admin_login(login_data: dict, db: AsyncSession = Depends(get_db)):
    """Specific login for admin to check privileges immediately"""
    print(f"👉 Login attempt for: {login_data.get('email')}")
    email = login_data.get("email")
    password = login_data.get("password")
    
    from app.core.security import verify_password
    
    print("👉 Querying User from DB...")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    print(f"👉 User found: {user is not None}")
    
    if not user:
        print("❌ User not found")
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    print("👉 Verifying password...")
    if not verify_password(password, user.hashed_password):
        print("❌ Invalid password")
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    print(f"👉 Is Superuser: {user.is_superuser}")
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not an admin user")
    
    # Create access token
    print("👉 Creating token...")
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "is_admin": True})
    
    return ApiResponse(
        success=True,
        data={
            "token": access_token,
            "userId": str(user.id),
            "email": user.email,
            "is_admin": True
        }
    )

# --- Dashboard Stats ---

@router.get("/stats", response_model=ApiResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Get system statistics"""
    
    # Count Users
    user_count = await db.scalar(select(func.count(User.id)))
    
    # Count Matches
    match_count = await db.scalar(select(func.count(Match.id)))
    live_match_count = await db.scalar(select(func.count(Match.id)).where(Match.status == 'live'))
    
    # Count Teams
    team_count = await db.scalar(select(func.count(Team.id)))

    # Count Leagues
    league_count = await db.scalar(select(func.count(League.id)))
    
    return ApiResponse(
        success=True,
        data={
            "users": user_count,
            "matches": match_count,
            "live_matches": live_match_count,
            "teams": team_count,
            "leagues": league_count,
            "system_status": "healthy" 
        }
    )

# --- Seeding Logic ---

async def run_seed_process():
    """Background task to seed data"""
    global SEED_STATUS
    SEED_STATUS["is_running"] = True
    SEED_STATUS["progress"] = 0
    SEED_STATUS["message"] = "Starting seed process..."
    SEED_STATUS["updated_at"] = datetime.utcnow().isoformat()
    
    try:
        # We need a new session since we are in a background task
        # But DataSyncService needs a session.
        # We'll creating a new session using sessionmaker from database.py directly or similar.
        # Importing here to avoid circulars if any
        from app.db.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            service = DataSyncService(db)
            
            # 1. Sync Leagues
            SEED_STATUS["message"] = "Syncing leagues..."
            SEED_STATUS["updated_at"] = datetime.utcnow().isoformat()
            await service.sync_leagues()
            
            # Get all leagues
            result = await db.execute(select(League))
            leagues = result.scalars().all()
            total_leagues = len(leagues)
            
            SEED_STATUS["total"] = total_leagues
            SEED_STATUS["message"] = f"Found {total_leagues} leagues. Starting match sync..."
            
            # 2. Sync Matches per league (Past 14 days + Future 14 days)
            today = date.today()
            date_from = (today - timedelta(days=14)).strftime("%Y-%m-%d")
            date_to = (today + timedelta(days=14)).strftime("%Y-%m-%d")
            
            processed = 0
            for league in leagues:
                try:
                    SEED_STATUS["message"] = f"Syncing {league.name}..."
                    await service.sync_matches_date_range(league.external_id, date_from, date_to)
                    # Also sync standings
                    await service.sync_standings(league.external_id)
                    
                except Exception as e:
                    logger.error(f"Error seeding league {league.name}: {e}")
                
                processed += 1
                SEED_STATUS["progress"] = int((processed / total_leagues) * 100)
                SEED_STATUS["updated_at"] = datetime.utcnow().isoformat()
                
                # Rate limit
                await asyncio.sleep(5) 

            SEED_STATUS["message"] = "Seed completed successfully!"
            SEED_STATUS["progress"] = 100
            
    except Exception as e:
        SEED_STATUS["message"] = f"Error: {str(e)}"
        logger.error(f"Seed process failed: {e}")
    finally:
        SEED_STATUS["is_running"] = False
        SEED_STATUS["updated_at"] = datetime.utcnow().isoformat()


@router.post("/seed", response_model=ApiResponse)
async def trigger_seed(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_superuser)
):
    """Trigger manual data seeding"""
    global SEED_STATUS
    if SEED_STATUS["is_running"]:
        return ApiResponse(success=False, message="Seed process is already running")
    
    background_tasks.add_task(run_seed_process)
    
    return ApiResponse(
        success=True, 
        message="Seed process started in background",
        data={"status": "running"}
    )

@router.get("/seed/active", response_model=ApiResponse)
async def get_seed_status(
    current_user: User = Depends(get_current_superuser)
):
    """Get status of active seed process"""
    return ApiResponse(
        success=True,
        data=SEED_STATUS
    )


# --- Match Management ---

@router.get("/matches", response_model=ApiResponse)
async def get_admin_matches(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Get all matches for admin (paginated)"""
    # Eager load Home and Away teams
    from sqlalchemy.orm import selectinload
    
    query = (
        select(Match)
        .options(selectinload(Match.home_team), selectinload(Match.away_team), selectinload(Match.league))
        .order_by(desc(Match.match_date))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    matches = result.scalars().all()
    
    return ApiResponse(
        success=True,
        data=[
            {
                "id": m.id,
                "date": m.match_date.isoformat(),
                "status": m.status,
                "home_team": m.home_team.name if m.home_team else "Unknown",
                "away_team": m.away_team.name if m.away_team else "Unknown",
                "home_score": m.home_score,
                "away_score": m.away_score,
                "league": m.league.name if m.league else "Unknown"
            }
            for m in matches
        ]
    )


@router.post("/matches", response_model=ApiResponse)
async def create_match(
    match_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Manually create a match"""
    try:
        new_match = Match(
            home_team_id=match_data.get("home_team_id"),
            away_team_id=match_data.get("away_team_id"),
            league_id=match_data.get("league_id"),
            match_date=datetime.fromisoformat(match_data.get("match_date")),
            status=match_data.get("status", "scheduled"),
            venue=match_data.get("venue"),
            round=match_data.get("round"),
            home_score=match_data.get("home_score"),
            away_score=match_data.get("away_score")
        )
        db.add(new_match)
        await db.commit()
        await db.refresh(new_match)
        return ApiResponse(success=True, data={"id": new_match.id}, message="Match created successfully")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/matches/{match_id}", response_model=ApiResponse)
async def update_match(
    match_id: int,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Update match details (score, status)"""
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    for key, value in update_data.items():
        if hasattr(match, key):
            if key == "match_date" and isinstance(value, str):
                setattr(match, key, datetime.fromisoformat(value))
            else:
                setattr(match, key, value)
                
    await db.commit()
    await db.refresh(match)
    return ApiResponse(success=True, message="Match updated successfully")

@router.delete("/matches/{match_id}", response_model=ApiResponse)
async def delete_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Delete a match"""
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    await db.delete(match)
    await db.commit()
    return ApiResponse(success=True, message="Match deleted successfully")

# --- User Management ---

@router.get("/users", response_model=ApiResponse)
async def get_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """List all users"""
    query = select(User).offset(skip).limit(limit).order_by(desc(User.created_at))
    result = await db.execute(query)
    users = result.scalars().all()
    
    return ApiResponse(
        success=True,
        data=[
            {
                "id": u.id,
                "email": u.email,
                "name": u.name,
                "is_active": u.is_active,
                "is_superuser": u.is_superuser,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ]
    )

@router.put("/users/{user_id}/status", response_model=ApiResponse)
async def update_user_status(
    user_id: int,
    status_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Activate/Deactivate user"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if "is_active" in status_data:
        user.is_active = status_data["is_active"]
        
    if "is_superuser" in status_data:
        # Prevent self-demotion if desired, but for now allow it
        user.is_superuser = status_data["is_superuser"]
        
    await db.commit()
    return ApiResponse(success=True, message=f"User status updated")


# --- Team Management ---

@router.get("/teams", response_model=ApiResponse)
async def get_admin_teams(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Get all teams for admin (paginated)"""
    query = select(Team).order_by(Team.name).offset(skip).limit(limit)
    result = await db.execute(query)
    teams = result.scalars().all()
    
    return ApiResponse(
        success=True,
        data=[
            {
                "id": t.id,
                "name": t.name,
                "short_name": t.short_name,
                "country": t.country,
                "logo": t.logo,
                "external_id": t.external_id
            }
            for t in teams
        ]
    )
