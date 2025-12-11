import { useState, useEffect } from 'react'
import { getCurrentWeekGames } from '../api/games'
import GameBox from '../components/GameBox'

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
      <h1>Fantasy Football</h1>
      <p>Welcome!</p>

      <div>
        <h2>NFL Week {week} Games</h2>
        {/* for each game in current week, post the GameBox component */}
        {/* want this div to be a table like structure */}
        <div>
          {games.map((game) => (
            <GameBox key={game.id} game={game}/>
          ))}
        </div>
      </div>
    </div>
  );
}
