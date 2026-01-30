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