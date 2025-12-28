import api from "./client";

export async function getGames(season, week) {
  const response = await api.get(`/games/?season=${season}&week=${week}`)
  return response.data
}

export async function getCurrentWeekGames() {
  const response = await api.get(`/games/currentWeek/`)
  return response.data
}

export const getGameById = async (gameId) => {
  const response = await api.get(`/games/${gameId}/`)
  return response.data
}