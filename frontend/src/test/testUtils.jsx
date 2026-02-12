import { render } from '@testing-library/react'
import { BrowserRouter, MemoryRouter } from 'react-router-dom'
import { ThemeProvider } from '../context/ThemeContext'

// Render with all providers
export function renderWithProviders(ui, { route = '/', ...options } = {}) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <ThemeProvider>
        {ui}
      </ThemeProvider>
    </MemoryRouter>,
    options
  )
}

// Render with just router (no theme context)
export function renderWithRouter(ui, { route = '/' } = {}) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      {ui}
    </MemoryRouter>
  )
}

// Mock game data
export const mockGame = {
  id: '2025_01_SF_KC',
  season: 2025,
  week: 1,
  date: '2025-01-15',
  time: '16:25',
  home_team: {
    id: 1,
    name: 'Kansas City Chiefs',
    abbreviation: 'KC',
    record: '10-2',
    logo_url: null,
  },
  away_team: {
    id: 2,
    name: 'San Francisco 49ers',
    abbreviation: 'SF',
    record: '9-3',
    logo_url: null,
  },
  home_score: 31,
  away_score: 24,
  location: 'GEHA Field',
  temp: 45,
  wind: 10,
}

export const mockUpcomingGame = {
  id: '2025_02_PHI_KC',
  season: 2025,
  week: 2,
  date: '2025-01-22',
  time: '13:00',
  home_team: {
    id: 1,
    name: 'Kansas City Chiefs',
    abbreviation: 'KC',
    record: '11-2',
    logo_url: null,
  },
  away_team: {
    id: 3,
    name: 'Philadelphia Eagles',
    abbreviation: 'PHI',
    record: '10-3',
    logo_url: null,
  },
  home_score: null,
  away_score: null,
  location: 'GEHA Field',
  temp: 38,
  wind: 15,
}

// Mock player data
export const mockPlayer = {
  id: '00-0033873',
  name: 'Patrick Mahomes',
  position: 'QB',
  team: 'KC',
  team_name: 'Kansas City Chiefs',
  image_url: null,
  status: 'ACT',
  stats: {
    avg_fantasy_points: 24.5,
    total_fantasy_points: 73.5,
    games_played: 3,
    avg_targets: 0,
    avg_receptions: 0,
    avg_receiving_yards: 0,
    avg_rush_attempts: 3.2,
    avg_rush_yards: 18.5,
    avg_pass_yards: 298.3,
  },
}

// Mock box score data
export const mockBoxScore = {
  game_id: '2025_01_SF_KC',
  home_team: {
    id: 1,
    abbreviation: 'KC',
    name: 'Kansas City Chiefs',
    logo_url: null,
    score: 31,
    stats: {
      passing: { attempts: 35, completions: 28, yards: 320, touchdowns: 3 },
      rushing: { attempts: 25, yards: 120, touchdowns: 1 },
      total_yards: 440,
      turnovers: 0,
      sacks: 1,
      penalties: 5,
      penalty_yards: 45,
    },
    top_performers: [
      {
        player_id: '00-0033873',
        name: 'Patrick Mahomes',
        position: 'QB',
        fantasy_points: 26.8,
        pass_yards: 320,
        pass_tds: 3,
        rush_yards: 25,
        rush_tds: 0,
        receptions: 0,
        receiving_yards: 0,
        receiving_tds: 0,
      },
    ],
  },
  away_team: {
    id: 2,
    abbreviation: 'SF',
    name: 'San Francisco 49ers',
    logo_url: null,
    score: 24,
    stats: {
      passing: { attempts: 32, completions: 22, yards: 265, touchdowns: 2 },
      rushing: { attempts: 22, yards: 98, touchdowns: 1 },
      total_yards: 363,
      turnovers: 1,
      sacks: 3,
      penalties: 7,
      penalty_yards: 55,
    },
    top_performers: [],
  },
}
