import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import { getGameById } from "../api/games"
import TeamStatsSection from "../components/TeamStatsSection"
import GameTitle from "../components/GameTitle"

export default function GameInfo() {
  const { gameId } = useParams()
  const [game, setGame] = useState(null)
  const [numGames, setNumGames] = useState(3)

  useEffect(() => {
    // use param 'gameId' to fetch game data (info)
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
      <GameTitle game={game}/>

      <div>
        <label>Show stats from last:</label>
        <select 
          value={numGames}
          onChange={(e) => setNumGames(Number(e.target.value))}
        >
          <option value={1}>1 game</option>
          <option value={3}>3 games</option>
          <option value={5}>5 games</option>
          <option value={10}>10 games</option>
        </select>
      </div>

      <div>
        <TeamStatsSection team={game.home_team} numGames={numGames}/>
        <TeamStatsSection team={game.away_team} numGames={numGames}/>    
      </div>
    </div>
  )
}
