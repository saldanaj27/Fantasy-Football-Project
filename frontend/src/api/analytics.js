import api from "./client";

/*
  Analytics APIs

  Output of Analytics Object: 
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

export async function getDefenseAllowed(numGames, teamId, position) {
  const response = await api.get(`analytics/defense-allowed/?games=${numGames}&team_id=${teamId}&position=${position}`)
  return response.data
}