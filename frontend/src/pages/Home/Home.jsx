import { useState, useEffect } from 'react'
import { getCurrentWeekGames } from '../../api/games'
import GameBox from './components/GameBox'
import './Home.css'

// home page should show all games
export default function Home() {
  const [week, setWeek] = useState(1)
  const [games, setGames] = useState([])

  useEffect(() => {
    const getCurrentWeek = async () => {
      const data = await getCurrentWeekGames()

      const sortedGames = [...data].sort((a, b) => {
        const dateA = new Date(`${a.date}T${a.time}`)
        const dateB = new Date(`${b.date}T${b.time}`)
        return dateA - dateB
      })

      setWeek(sortedGames[0]?.week)
      setGames(sortedGames)
    }

    getCurrentWeek()
  }, [])
  
  return (
    <div>
      <div className="home-container">
      <h1 className="home-title">Fantasy Football</h1>
      <p className="home-subtitle">Welcome!</p>

      <h2 className="week-title">NFL Week {week} Games</h2>
        {/* for each game in current week, post the GameBox component */}
        {/* want this div to be a table like structure */}
        <div className="games-grid">
          {games.map((game) => (
            <GameBox key={game.id} game={game}/>
          ))}
        </div>
      </div>
    </div>
  );
}
