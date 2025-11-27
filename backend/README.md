# ScoreFlow Backend - Setup & Usage Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Football API Key (football-data.org or RapidAPI)

## Quick Start with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Manual Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# or
source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key
- `FOOTBALL_API_KEY`: API key from football-data.org

### 3. Initialize Database

```bash
# Start PostgreSQL
docker run -d -p 5432:5432 \
  -e POSTGRES_DB=scoreflow \
  -e POSTGRES_USER=scoreflow \
  -e POSTGRES_PASSWORD=password \
  postgres:15-alpine

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine
```

### 4. Seed Initial Data

```bash
# Sync leagues from API
python -m app.cli sync-leagues

# Sync matches for Premier League (ID: 2021)
python -m app.cli sync-matches 2021 14

# Or seed all popular leagues
python -m app.cli seed
```

### 5. Run Development Server

```bash
uvicorn main:app --reload --port 8000
```

API will be available at:
- Main: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## CLI Commands

```bash
# Sync all leagues
python -m app.cli sync-leagues

# Sync matches for a league (league_id, days_ahead)
python -m app.cli sync-matches 2021 7

# Update live match scores
python -m app.cli update-live

# Seed initial data
python -m app.cli seed
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user

### Matches
- `GET /api/v1/matches/upcoming` - Get upcoming matches
- `GET /api/v1/matches/live` - Get live matches
- `GET /api/v1/matches/finished` - Get finished matches
- `GET /api/v1/matches/{id}` - Get match details
- `GET /api/v1/matches/{id}/prediction` - Get ML prediction
- `GET /api/v1/matches/h2h` - Head-to-head stats

### Leagues
- `GET /api/v1/leagues` - Get all leagues
- `GET /api/v1/leagues/{id}` - Get league details
- `GET /api/v1/leagues/{id}/standings` - Get standings

### Teams
- `GET /api/v1/teams/{id}` - Get team details
- `GET /api/v1/teams/search?q=` - Search teams
- `GET /api/v1/teams/{id}/stats` - Get team statistics

### Predictions
- `GET /api/v1/predictions/{match_id}` - Get match prediction

## ML Model Training (TODO)

```bash
# Train prediction model
python -m app.ml.train --data data/matches.csv --output models/prediction_model.pkl
```

## Scheduled Tasks

Use Celery for background tasks:

```bash
# Start Celery worker
celery -A app.tasks worker --loglevel=info

# Start Celery beat (scheduler)
celery -A app.tasks beat --loglevel=info
```

Tasks:
- Update live matches every 30 seconds
- Sync new matches daily
- Send notifications for followed matches

## Production Deployment

### Using Docker

```bash
docker build -t scoreflow-api .
docker run -d -p 8000:8000 \
  -e DATABASE_URL=... \
  -e REDIS_URL=... \
  scoreflow-api
```

### Using systemd

```ini
[Unit]
Description=ScoreFlow API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/scoreflow/backend
Environment="PATH=/var/www/scoreflow/backend/.venv/bin"
ExecStart=/var/www/scoreflow/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Monitoring

- Health check: `GET /health`
- Metrics: Add Prometheus metrics
- Logging: Configure structured logging

## Troubleshooting

### API Rate Limiting
Football-Data.org free tier: 10 requests/minute
- Use Redis cache to minimize API calls
- Implement request queuing

### Database Performance
- Add indexes on frequently queried columns
- Use connection pooling
- Monitor slow queries

### ML Model Issues
- If model not found, system uses baseline Elo-based predictions
- Train model with historical data for better accuracy
