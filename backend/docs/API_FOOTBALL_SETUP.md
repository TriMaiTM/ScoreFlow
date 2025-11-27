# API-Football Integration Setup

## Overview
ScoreFlow integrates with **API-Football.com** to provide enhanced data including:
- ⚽ Detailed team statistics (possession, shots, xG)
- 📊 Match statistics and events
- 🤕 Player injuries
- 🔮 AI-powered predictions
- 📈 Advanced analytics

## Free Tier Limits
- **100 requests/day**
- All leagues and competitions
- Historical data available

## Setup Instructions

### 1. Get Your API Key

1. Visit: https://www.api-football.com/
2. Click **"Sign Up"** (top right)
3. Create account with email
4. Go to **Dashboard** → **My Access**
5. Copy your **API Key** (looks like: `abc123def456...`)

### 2. Configure Environment

Add to your `.env` file:

```bash
# API-Football.com (100 requests/day free)
API_FOOTBALL_KEY=your_actual_api_key_here
API_FOOTBALL_ENABLED=true
```

**Example:**
```bash
API_FOOTBALL_KEY=7a4f8e2c91d6b5a3f8e2c91d6b5a3f8e
API_FOOTBALL_ENABLED=true
```

### 3. Restart Backend

```bash
cd backend

# If using uvicorn directly
uvicorn main:app --reload

# If using docker
docker-compose restart backend
```

### 4. Verify Setup

Check API status:
```bash
curl http://localhost:8000/api/v1/enhanced/api-status
```

Expected response:
```json
{
  "success": true,
  "data": {
    "enabled": true,
    "requests": {
      "current": 5,
      "limit_day": 100
    }
  }
}
```

## Available Enhanced Endpoints

### Team Statistics
```bash
GET /api/v1/enhanced/teams/{team_id}/statistics?league_id=39&season=2024
```

**Response includes:**
- Form (last 5 matches: WWDLW)
- Goals scored/conceded averages
- Win/Draw/Loss counts
- Clean sheets
- Cards statistics

### Match Statistics (Live/Finished)
```bash
GET /api/v1/enhanced/matches/{match_id}/statistics?external_fixture_id=12345
```

**Response includes:**
- Ball possession
- Shots on/off target
- Corners
- Fouls
- Offsides

### Head-to-Head Detailed
```bash
GET /api/v1/enhanced/matches/h2h-detailed?team1_id=33&team2_id=34&last=10
```

**Response includes:**
- Last 10 H2H matches
- Score details
- Venue information
- Date and competition

### Team Injuries
```bash
GET /api/v1/enhanced/teams/{team_id}/injuries?league_id=39&season=2024
```

**Response includes:**
- Injured players list
- Injury type and reason
- Expected return date

### AI Predictions
```bash
GET /api/v1/enhanced/matches/{match_id}/ai-prediction?external_fixture_id=12345
```

**Response includes:**
- Win probabilities (home/draw/away)
- Predicted score
- Betting advice
- Comparison metrics

## Request Management

### Daily Limit: 100 requests

**Strategy to maximize:**

1. **Cache aggressively** (already implemented)
   - Team stats: 1 hour cache
   - H2H: 6 hours cache
   - Predictions: 24 hours cache

2. **Prioritize requests:**
   - ✅ Use for upcoming matches (predictions)
   - ✅ Use for live matches (statistics)
   - ❌ Don't fetch for old finished matches

3. **Fallback to database:**
   - Calculate basic stats from existing data
   - Only fetch from API when needed

### Monitor Usage

Check remaining requests:
```bash
curl http://localhost:8000/api/v1/enhanced/api-status
```

## Mapping External IDs

API-Football uses different IDs than football-data.org. You need to map them:

### Popular Leagues:
| Competition | Football-Data ID | API-Football ID |
|-------------|------------------|-----------------|
| Premier League | 2021 | 39 |
| La Liga | 2014 | 140 |
| Bundesliga | 2002 | 78 |
| Serie A | 2019 | 135 |
| Ligue 1 | 2015 | 61 |
| Champions League | 2001 | 2 |

### Teams (Premier League):
| Team | API-Football ID |
|------|----------------|
| Manchester United | 33 |
| Liverpool | 40 |
| Arsenal | 42 |
| Chelsea | 49 |
| Manchester City | 50 |
| Tottenham | 47 |

*Note: For full mapping, use the API-Football teams endpoint*

## Troubleshooting

### "API key not configured"
- Check `.env` file has `API_FOOTBALL_KEY`
- Restart backend after adding key

### "Rate limit exceeded"
- Wait until next day (resets at 00:00 UTC)
- Check usage: `GET /api/v1/enhanced/api-status`

### "Invalid API key"
- Verify key copied correctly (no spaces)
- Check key is active in API-Football dashboard

### Statistics not available
- Match might not exist in API-Football
- Try with `external_fixture_id` parameter
- Check if match is too old

## Cost Optimization

**Free tier is enough for development**, but for production:

### Upgrade Options:
- **Basic**: $15/month - 3,000 req/day
- **Pro**: $40/month - 15,000 req/day
- **Ultra**: $80/month - 45,000 req/day

### Alternative: Web Scraping
If you exceed limits, consider scraping:
- SofaScore (live scores)
- Understat (xG data)
- FBref (player stats)

*See `docs/WEB_SCRAPING.md` for implementation*

## Integration with ML Model

Enhanced data improves prediction accuracy:

```python
# backend/app/ml/features.py

async def get_enhanced_features(match, db):
    # Get team stats from API-Football
    home_stats = await enhanced_service.get_team_statistics(
        match.home_team_id, 
        match.league_id, 
        2024, 
        db
    )
    
    # Extract features
    features = {
        'home_form_points': calculate_form_points(home_stats['form']),
        'home_goals_avg': float(home_stats['goals']['for']['average']['total']),
        'home_conceded_avg': float(home_stats['goals']['against']['average']['total']),
        # ... more features
    }
    
    return features
```

## Support

- API Docs: https://www.api-football.com/documentation-v3
- Support: support@api-football.com
- Status: https://status.api-football.com/

## License

API-Football data usage must comply with their Terms of Service:
- ✅ Personal projects
- ✅ Commercial apps (with paid plan)
- ❌ Data reselling
- ❌ Creating competing API services
