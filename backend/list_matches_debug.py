
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy import text
from dotenv import load_dotenv

# Try loading from backend/.env
load_dotenv("backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    load_dotenv(r"d:\HK7\DACN2\ScoreFlow\backend\.env")
    DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Define minimal models to avoid import errors
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

Base = declarative_base()

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    match_date = Column(DateTime)
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])

async def list_matches():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        pass 
    
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        print("Finding Benfica vs Famalicao...")
        stmt = select(Match).options(selectinload(Match.home_team), selectinload(Match.away_team)).limit(100)
        result = await session.execute(stmt)
        matches = result.scalars().all()
        
        found = False
        for m in matches:
            if "Benfica" in m.home_team.name or "Benfica" in m.away_team.name:
                print(f"ID: {m.id} | {m.home_team.name} vs {m.away_team.name} | {m.match_date}")
                found = True
        
        if not found:
            print("Benfica match not found in first 100. Listing first 5 matches:")
            for m in matches[:5]:
                print(f"ID: {m.id} | {m.home_team.name} vs {m.away_team.name}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(list_matches())
