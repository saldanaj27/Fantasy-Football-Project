import api from "./client"

/*
  Search players with stats
  Query params: search, position, team, games, limit

  Response:
  {
    count: <int>,
    players: [{
      id, name, position, team, team_name, image_url, status,
      stats: { avg_fantasy_points, total_fantasy_points, games_played, ... }
    }]
  }
*/
export async function searchPlayers(params = {}) {
  const queryParams = new URLSearchParams()

  if (params.search) queryParams.append('search', params.search)
  if (params.position) queryParams.append('position', params.position)
  if (params.team) queryParams.append('team', params.team)
  if (params.games) queryParams.append('games', params.games)
  if (params.limit) queryParams.append('limit', params.limit)

  const response = await api.get(`players/search/?${queryParams.toString()}`)
  return response.data
}

/*
  Get all teams for filter dropdown
*/
export async function getTeams() {
  const response = await api.get('teams/')
  return response.data
}
