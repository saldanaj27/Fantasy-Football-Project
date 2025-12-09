import api from "./client";

export async function getTeams() {
  const response = await api.get("/teams");
  return response.data;
}