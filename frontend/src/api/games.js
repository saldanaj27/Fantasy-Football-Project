import api from "./client";

export async function getGames(season, week) {
  const response = await api.get(`/games/?season=${season}&week=${week}`);
  return response.data;
}