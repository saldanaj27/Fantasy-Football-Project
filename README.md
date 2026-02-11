# StatStack

A full-stack fantasy football analytics platform that provides comprehensive NFL statistics, player comparisons, and matchup insights to help you make smarter fantasy decisions.

## Features

- **Live Scores** - Track all NFL games with live scores, weather conditions, and game status
- **Player Search** - Find any player and view their fantasy performance, trends, and advanced metrics
- **Fantasy Rankings** - Weekly rankings by position with detailed stats (PPR scoring)
- **Start/Sit Tool** - Compare players head-to-head with matchup analysis
- **Team Stats** - Offensive and defensive statistics with configurable game ranges
- **Defense vs Position** - See how defenses perform against specific positions
- **Advanced Metrics** - Snap counts, target share, air yards, aDOT, YAC, and red zone stats
- **Light/Dark Mode** - Automatic theme switching based on time of day

## Tech Stack

### Backend
- **Django 4.2** - Python web framework
- **Django REST Framework** - RESTful API
- **PostgreSQL** - Primary database
- **Redis** - Caching layer
- **Celery** - Background task processing
- **nflreadpy** - NFL data source

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool
- **React Router** - Client-side routing
- **Recharts** - Data visualization
- **Axios** - HTTP client

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Local development orchestration

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Fantasy-Football-Project.git
   cd Fantasy-Football-Project
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   # Edit both .env files with your configuration
   ```

3. **Start database services**
   ```bash
   docker-compose up -d
   ```

4. **Backend setup**
   ```bash
   cd backend
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

5. **Frontend setup** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/api/

### Data Seeding

Load NFL data using the management commands:

```bash
cd backend

# Seed teams (required first)
python manage.py seed_teams

# Seed players
python manage.py seed_players

# Seed game schedules (supports multiple years)
python manage.py seed_games --start-year 2020 --end-year 2025

# Seed player and team stats
python manage.py seed_stats --start-year 2020 --end-year 2025
```

## Project Structure

```
Fantasy-Football-Project/
├── backend/
│   ├── api/                 # API endpoints and serializers
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── viewsets/
│   │       └── analytics.py # Advanced analytics endpoints
│   ├── games/               # Game model and management
│   ├── players/             # Player model
│   ├── stats/               # Player and team statistics
│   ├── teams/               # Team model
│   ├── predictions/         # ML prediction pipeline
│   │   ├── features.py      # Feature extraction
│   │   ├── ml_models.py     # ML models (winner, spread, total)
│   │   ├── services.py      # PredictionService singleton
│   │   └── trained_models/  # Saved model files (not in git)
│   └── untitled_football_project/  # Django settings
│
├── frontend/
│   ├── src/
│   │   ├── api/             # API client functions
│   │   ├── components/      # Reusable components
│   │   │   ├── NavBar/      # Navigation with theme toggle
│   │   │   └── ErrorBoundary/ # Global error boundary
│   │   ├── context/         # React context (ThemeContext)
│   │   ├── pages/           # Page components
│   │   │   ├── Landing/     # Home landing page
│   │   │   ├── Scores/      # Weekly games view
│   │   │   ├── GameInfo/    # Game detail with tabs
│   │   │   ├── Players/     # Player search
│   │   │   ├── Rankings/    # Fantasy rankings
│   │   │   ├── StartSit/    # Player comparison
│   │   │   └── NotFound/    # 404 page
│   │   └── styles/          # Global CSS (theme variables)
│   └── index.html
│
├── nginx/                   # Production nginx config
├── .github/workflows/       # CI/CD (ci.yml, deploy.yml)
├── docker-compose.yml       # Dev: PostgreSQL + Redis
├── docker-compose.prod.yml  # Prod: full stack with nginx
└── Dockerfile               # Backend container
```

## API Endpoints

### Core Resources
- `GET /api/teams/` - List all teams
- `GET /api/players/` - List players (with filters)
- `GET /api/games/` - List games by week/season
- `GET /api/games/currentWeek` - Current week's games

### Analytics
- `GET /api/analytics/recent-stats?team_id=X&games=N` - Team stats over last N games
- `GET /api/analytics/defense-allowed?team_id=X&position=RB` - Defense vs position stats
- `GET /api/analytics/player-stats?team_id=X` - Players with advanced metrics
- `GET /api/analytics/usage-metrics?team_id=X` - Pass/run splits, target shares
- `GET /api/analytics/player-comparison?player_id=X` - Player comparison data

## Environment Variables

### Backend (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/1
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api/
```

## Theme System

StatStack features automatic light/dark mode based on time of day:
- **Light Mode**: 6 AM - 6 PM
- **Dark Mode**: 6 PM - 6 AM

Users can manually toggle the theme using the sun/moon icon in the navigation bar. The preference is saved to localStorage.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational purposes. NFL data is sourced from nflreadpy.

## Acknowledgments

- [nflreadpy](https://github.com/nflverse/nflverse-data) for NFL statistics data
- [Recharts](https://recharts.org/) for charting library
