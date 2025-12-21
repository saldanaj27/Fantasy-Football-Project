import { useState, useEffect } from 'react'
import { getCurrentWeekGames } from '../api/games'
import GameBox from '../components/GameBox'
import './Home.css'

// home page should show all games
export default function Home() {
  const [week, setWeek] = useState(1)
  const [games, setGames] = useState([])

  const getCurrentWeek = async () => {
    const data = await getCurrentWeekGames()
    setWeek(data[0].week)
    setGames(data)
  }

  useEffect(() => {
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
