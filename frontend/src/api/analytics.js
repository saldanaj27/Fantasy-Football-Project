import api from "./client";

/*
  Analytics APIs

  Output of /api/analytics/recent-stats API:
  Param: games (default=3), team_id

  {
    'team_id': <team_id>,
    'passing': <passing_object>, (attempts, total_yards_average, touchdowns, completion_percentage)
    'rushing': <rushing_object>, (attempts, total_yards_average, touchdowns)
    'total_yards_per_game': <float>,
    'off_turnovers_total': <int>,
    "def_turnovers_total": <int>,
    "points_per_game": <float>
  }
*/
export async function getRecentStats(numGames, teamId) {
  const response = await api.get(`analytics/recent-stats/?games=${numGames}&team_id=${teamId}`)
  return response.data
}

/*
  Output of /api/analytics/defense-allowed API:
  Param: games (default=3), team_id, position (default='RB')

  {
    'team_id': <team_id>,
    'position': <string>, (RB, TE, WR, QB)
    'games_analyzed': <int>,
    'rushing': <rushing_object>, (attempts, yards, touchdowns)
    'receiving': <receiving object>, (targets, receptions, yards, touchdowns)
    'fantasy_points': <float>,
    'total_yards_allowed': <float>
  }

*/
export async function getDefenseAllowed(numGames, teamId, position) {
  const response = await api.get(`analytics/defense-allowed/?games=${numGames}&team_id=${teamId}&position=${position}`)
  return response.data
}

/*
  Output of /api/analytics/player-stats API:
  Param: games (default=3), team_id

  {
    'team_id': <team_id>,
    'games_analyzed': <int>,
    'players': {
      'QB': [{ player_id, name, position, stats: {...}, games_played }],
      'RB': [...],
      'WR': [...],
      'TE': [...]
    }
  }
*/
export async function getPlayerStats(numGames, teamId) {
  const response = await api.get(`analytics/player-stats/?games=${numGames}&team_id=${teamId}`)
  return response.data
}

/*
  Output of /api/analytics/usage-metrics API:
  Param: games (default=3), team_id

  {
    'team_id': <team_id>,
    'games_analyzed': <int>,
    'pass_run_split': { pass_attempts, rush_attempts, pass_percentage, rush_percentage },
    'target_share': [{ player_id, name, position, targets, target_share_percentage }],
    'carry_share': [{ player_id, name, position, rush_attempts, carry_share_percentage }]
  }
*/
export async function getUsageMetrics(numGames, teamId) {
  const response = await api.get(`analytics/usage-metrics/?games=${numGames}&team_id=${teamId}`)
  return response.data
}

/*
  Output of /api/analytics/player-comparison API:
  Param: player_id, games (default=3)

  Returns player stats + upcoming matchup + opponent defense ranking
*/
export async function getPlayerComparison(playerId, numGames = 3) {
  const response = await api.get(`analytics/player-comparison/?player_id=${playerId}&games=${numGames}`)
  return response.data
}

/*
  Output of /api/analytics/game-box-score API:
  Param: game_id (required)

  Returns box score stats for a finished game:
  {
    'game_id': <int>,
    'home_team': {
      'id': <int>,
      'abbreviation': <string>,
      'name': <string>,
      'score': <int>,
      'stats': { passing, rushing, total_yards, turnovers, sacks, penalties },
      'top_performers': [{ player_id, name, position, fantasy_points, ... }]
    },
    'away_team': { same structure }
  }
*/
export async function getGameBoxScore(gameId) {
  const response = await api.get(`analytics/game-box-score/?game_id=${gameId}`)
  return response.data
}

export async function getTeamGameLog(teamId, numGames = 5) {
  const response = await api.get(`analytics/team-game-log/?team_id=${teamId}&games=${numGames}`)
  return response.data
}

export async function getHeadToHead(team1Id, team2Id, limit = 5) {
  const response = await api.get(`analytics/head-to-head/?team1_id=${team1Id}&team2_id=${team2Id}&limit=${limit}`)
  return response.data
}

export async function getCommonOpponents(team1Id, team2Id, season) {
  const response = await api.get(`analytics/common-opponents/?team1_id=${team1Id}&team2_id=${team2Id}&season=${season}`)
  return response.data
}

export async function getUsageTrends(teamId, numGames = 5) {
  const response = await api.get(`analytics/usage-trends/?team_id=${teamId}&games=${numGames}`)
  return response.data
}

export async function getPlayerTrend(playerId, numGames = 10) {
  const response = await api.get(`analytics/player-trend/?player_id=${playerId}&games=${numGames}`)
  return response.data
}

export async function getBestTeam(numGames = 3) {
  const response = await api.get(`analytics/best-team/?games=${numGames}`)
  return response.data
}