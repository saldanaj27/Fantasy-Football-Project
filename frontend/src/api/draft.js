import client from './client'

export async function createDraftSession({ num_teams, num_rounds, user_team_position, scoring_format }) {
  const { data } = await client.post('/draft/create/', {
    num_teams,
    num_rounds,
    user_team_position,
    scoring_format,
  })
  return data
}

export async function makePick(sessionId, playerId) {
  const { data } = await client.post(`/draft/${sessionId}/pick/`, {
    player_id: playerId,
  })
  return data
}

export async function getDraftBoard(sessionId) {
  const { data } = await client.get(`/draft/${sessionId}/board/`)
  return data
}

export async function getAvailablePlayers(sessionId, { position, search } = {}) {
  const params = {}
  if (position) params.position = position
  if (search) params.search = search
  const { data } = await client.get(`/draft/${sessionId}/available/`, { params })
  return data
}

export async function getUserRoster(sessionId) {
  const { data } = await client.get(`/draft/${sessionId}/roster/`)
  return data
}
