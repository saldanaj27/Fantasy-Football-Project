import api from "./client";

/*
  Predictions API

  These endpoints provide ML-based game predictions.
  Only available for upcoming (not yet played) games.

  Prediction Object Structure:
  {
    "game_id": "2025_10_KC_BUF",
    "home_team": "BUF",
    "away_team": "KC",
    "game_date": "2025-11-02",
    "prediction": {
      "home_win_probability": 0.523,
      "predicted_winner": "home",
      "predicted_spread": 1.2,
      "predicted_total": 51.5,
      "predicted_home_score": 26.4,
      "predicted_away_score": 25.1,
      "confidence": "medium"
    },
    "model_version": "v20260206_013321"
  }
*/

// GET prediction for a specific game
export async function getGamePrediction(gameId) {
  try {
    const response = await api.get(`/predictions/game/?game_id=${gameId}`)
    return response.data
  } catch (error) {
    // Return null if prediction not available (e.g., game already played)
    console.warn('Prediction not available:', error.response?.data?.error || error.message)
    return null
  }
}

// GET predictions for all games in a week
export async function getWeekPredictions(season, week) {
  try {
    const response = await api.get(`/predictions/week/?season=${season}&week=${week}`)
    return response.data
  } catch (error) {
    console.warn('Week predictions not available:', error.response?.data?.error || error.message)
    return null
  }
}

// GET model info (version, accuracy, etc.)
export async function getModelInfo() {
  try {
    const response = await api.get('/predictions/model-info/')
    return response.data
  } catch (error) {
    console.warn('Model info not available:', error.response?.data?.error || error.message)
    return null
  }
}
