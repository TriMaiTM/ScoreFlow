# ScoreFlow

Ứng dụng di động React Native để theo dõi lịch thi đấu bóng đá, dự đoán kết quả bằng AI, và nhận thông báo real-time.

## Tech Stack

### Frontend (Mobile App)
- **Framework**: React Native + TypeScript với Expo
- **State Management**: Redux Toolkit + Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Navigation**: React Navigation v6
- **UI Library**: React Native Paper
- **Notifications**: Expo Notifications
- **Offline Support**: AsyncStorage + NetInfo

### Backend (API)
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL + SQLAlchemy (async)
- **Cache**: Redis
- **Authentication**: JWT (python-jose)
- **ML Models**: scikit-learn, XGBoost, LightGBM

## Project Structure

```
ScoreFlow/
├── src/                    # Frontend source code
│   ├── screens/           # Screen components
│   ├── navigation/        # Navigation setup
│   ├── services/          # API client, notifications, cache
│   ├── store/             # Redux slices & Zustand stores
│   ├── types/             # TypeScript types
│   └── theme/             # Theme configuration
├── backend/               # Backend API
│   ├── app/
│   │   ├── api/v1/       # API endpoints
│   │   ├── core/         # Config, security
│   │   ├── db/           # Database models
│   │   └── schemas/      # Pydantic schemas
│   └── main.py           # FastAPI app entry
└── App.tsx               # Root component
```

## Setup & Installation

### Frontend Setup

1. **Install dependencies**:
```bash
npm install
# or
yarn install
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env với API keys của bạn
```

3. **Run development server**:
```bash
npm start
# or
npx expo start
```

4. **Run on device**:
- Android: `npm run android` hoặc scan QR code với Expo Go
- iOS: `npm run ios` hoặc scan QR code với Expo Go

### Backend Setup

1. **Create virtual environment**:
```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Setup database**:
```bash
# Install PostgreSQL và tạo database
# Cập nhật DATABASE_URL trong .env
cp .env.example .env
```

4. **Run development server**:
```bash
uvicorn main:app --reload --port 8000
```

API sẽ chạy tại: `http://localhost:8000`  
API Docs: `http://localhost:8000/docs`

## Features

### Implemented
- Cross-platform mobile app (iOS/Android)
- User authentication (JWT)
- Match listings (upcoming, live, finished)
- League standings
- Push notifications setup
- Offline-first caching
- Dark/Light theme
- Responsive UI with React Native Paper

### TODO / In Progress
- ML prediction model training & serving
- Team statistics & head-to-head
- Real-time match updates (webhooks)
- Advanced search & filters
- Favorite teams/matches
- Calendar integration
- Unit & E2E tests
- Docker deployment
- CI/CD pipeline

## ML Prediction Pipeline

The prediction module uses:
- **Features**: Elo ratings, form (last 5 matches), goals avg, H2H stats, home/away advantage, days since last match, injuries
- **Models**: XGBoost (baseline), LightGBM, or Neural Networks
- **Training**: Batch training on historical match data
- **Serving**: FastAPI endpoint with cached predictions

## Security

- JWT tokens stored in Expo SecureStore
- Password hashing with bcrypt
- Rate limiting on API endpoints (TODO)
- CORS configuration
- Environment variables for secrets

## API Endpoints

```
POST   /api/v1/auth/register       - User registration
POST   /api/v1/auth/login          - User login
GET    /api/v1/matches/upcoming    - Get upcoming matches
GET    /api/v1/matches/live        - Get live matches
GET    /api/v1/matches/{id}        - Get match details
GET    /api/v1/matches/{id}/prediction - Get ML prediction
GET    /api/v1/leagues             - Get all leagues
GET    /api/v1/leagues/{id}/standings - Get league standings
GET    /api/v1/teams/{id}          - Get team details
GET    /api/v1/teams/{id}/stats    - Get team statistics
```

## Testing

```bash
# Frontend tests
npm test

# Backend tests
cd backend
pytest
```

## Build & Deploy

### Frontend
```bash
# Build APK (Android)
eas build --platform android

# Build IPA (iOS)
eas build --platform ios
```

### Backend
```bash
# Docker build
docker build -t scoreflow-api ./backend
docker run -p 8000:8000 scoreflow-api
```



