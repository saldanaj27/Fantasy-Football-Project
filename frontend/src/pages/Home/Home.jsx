import { useState, useEffect } from 'react'
import { getCurrentWeekGames, getGames } from '../../api/games'
import GameBox from './components/GameBox'
import './Home.css'

// home page should show all games
export default function Home() {
  const [week, setWeek] = useState(1)
  const [season, setSeason] = useState(2025)
  const [games, setGames] = useState([])
  const [loading, setLoading] = useState(true)

  // Initialize with current week
  useEffect(() => {
    const getCurrentWeek = async () => {
      setLoading(true)
      const data = await getCurrentWeekGames()

      const sortedGames = [...data].sort((a, b) => {
        const dateA = new Date(`${a.date}T${a.time}`)
        const dateB = new Date(`${b.date}T${b.time}`)
        return dateA - dateB
      })

      if (sortedGames.length > 0) {
        setWeek(sortedGames[0].week)
        setSeason(sortedGames[0].season)
        setGames(sortedGames)
      }
      setLoading(false)
    }

    getCurrentWeek()
  }, [])

  // Fetch games when week changes
  useEffect(() => {
    if (week && season) {
      const fetchGames = async () => {
        setLoading(true)
        const data = await getGames(season, week)

        const sortedGames = [...data].sort((a, b) => {
          const dateA = new Date(`${a.date}T${a.time}`)
          const dateB = new Date(`${b.date}T${b.time}`)
          return dateA - dateB
        })

        setGames(sortedGames)
        setLoading(false)
      }

      fetchGames()
    }
  }, [week, season])
  
  return (
    <div>
      <div className="home-container">
        <h1 className="home-title">Fantasy Football</h1>
        <p className="home-subtitle">Welcome!</p>

        <div className="week-selector">
          <label htmlFor="week-select">Select Week:</label>
          <select
            id="week-select"
            value={week}
            onChange={(e) => setWeek(Number(e.target.value))}
          >
            {[...Array(22)].map((_, i) => (
              <option key={i + 1} value={i + 1}>
                Week {i + 1}
              </option>
            ))}
          </select>
        </div>

        <h2 className="week-title">NFL Week {week} Games</h2>

        {loading ? (
          <div className="loading-text">Loading games...</div>
        ) : games.length > 0 ? (
          <div className="games-grid">
            {games.map((game) => (
              <GameBox key={game.id} game={game}/>
            ))}
          </div>
        ) : (
          <div className="no-games-text">No games found for this week.</div>
        )}
      </div>
    </div>
  );
}
