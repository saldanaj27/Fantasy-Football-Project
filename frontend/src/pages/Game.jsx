import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import { getGameById } from "../api/games"

export default function Game() {
  const { gameId } = useParams()
  const [game, setGame] = useState(null)

  useEffect(() => {
    const fetchGame = async () => {
      const data = await getGameById(gameId)
      setGame(data)
    }
    fetchGame()
  }, [gameId])

  if (!game) {
    return <div>Loading game...</div>
  }

  return (
    <div>
      <h2>
        {game.away_team.abbreviation} @ {game.home_team.abbreviation}
      </h2>

      <p>Date: {game.date}</p>
      <p>Time: {game.time}</p>

      <p>
        Score: {game.away_score} - {game.home_score}
      </p>
    </div>
  )
}
