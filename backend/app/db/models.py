from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    avatar_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    
    # Relationships
    favorite_teams = relationship("FavoriteTeam", back_populates="user")
    followed_matches = relationship("FollowedMatch", back_populates="user")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    short_name = Column(String)
    logo = Column(String)
    country = Column(String)
    external_id = Column(Integer, unique=True)  # ID from external API


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String)
    logo = Column(String)
    season = Column(Integer)
    external_id = Column(Integer, unique=True)


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    league_id = Column(Integer, ForeignKey("leagues.id"))
    match_date = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, live, finished, postponed, cancelled
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    venue = Column(String)
    round = Column(String)
    external_id = Column(Integer, unique=True)
    
    # Relationships
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    league = relationship("League")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True)
    home_win_probability = Column(Float)
    draw_probability = Column(Float)
    away_win_probability = Column(Float)
    predicted_home_score = Column(Integer)
    predicted_away_score = Column(Integer)
    confidence = Column(Float)
    features = Column(JSON)  # Store feature values used for prediction
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    match = relationship("Match")


class TeamStats(Base):
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    season = Column(Integer)
    form = Column(String)  # Last 5 matches: W/D/L
    goals_scored = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    matches_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    elo_rating = Column(Float, default=1500.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    team = relationship("Team")


class FavoriteTeam(Base):
    __tablename__ = "favorite_teams"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    
    # Relationships
    user = relationship("User", back_populates="favorite_teams")
    team = relationship("Team")


class FollowedMatch(Base):
    __tablename__ = "followed_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))
    notification_sent = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="followed_matches")
    match = relationship("Match")


class Standing(Base):
    __tablename__ = "standings"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    season = Column(Integer)
    
    position = Column(Integer)
    played = Column(Integer, default=0)
    won = Column(Integer, default=0)
    drawn = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    goal_difference = Column(Integer, default=0)
    points = Column(Integer, default=0)
    
    form = Column(String)  # Last 5 matches: W/D/L
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    league = relationship("League")
    team = relationship("Team")


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(String)
    url = Column(String, unique=True, index=True)
    image_url = Column(String)
    source = Column(String)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
