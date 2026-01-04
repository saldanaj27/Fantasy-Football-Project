import api from "./client";

export async function getRecentStats(numGames, teamId) {
  const response = await api.get(`analytics/recent-stats/?games=${numGames}&team_id=${teamId}`)
  return response.data
}

export async function getDefenseAllowed(numGames, teamId, position) {
  const response = await api.get(`analytics/defense-allowed/?games=${numGames}&team_id=${teamId}&position=${position}`)
  return response.data
}