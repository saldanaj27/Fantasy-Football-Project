import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getCurrentWeekGames, getGames } from '../../api/games'
import GameBox from './components/GameBox'
import './Home.css'

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
    <div className="home-page">
      {/* Top Navigation */}
      <nav className="top-nav">
        <span className="brand">FANTASY FOOTBALL</span>
        <div className="nav-links">
          <Link to="/" className="nav-link active">Scores</Link>
          <Link to="/players" className="nav-link">Players</Link>
        </div>
      </nav>

      {/* Main Content */}
      <div className="home-content">
        {/* Week Selector Bar */}
        <div className="week-bar">
          <h2 className="week-bar-title">NFL Week {week}</h2>
          <div className="week-selector">
            <label htmlFor="week-select">Week:</label>
            <select
              id="week-select"
              value={week}
              onChange={(e) => setWeek(Number(e.target.value))}
            >
              {[...Array(22)].map((_, i) => (
                <option key={i + 1} value={i + 1}>
                  {i + 1}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Games Grid */}
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
          </div>
        ) : games.length > 0 ? (
          <div className="games-grid">
            {games.map((game) => (
              <GameBox key={game.id} game={game} />
            ))}
          </div>
        ) : (
          <div className="no-games">
            <div className="no-games-icon">🏈</div>
            <div className="no-games-text">No games scheduled for Week {week}</div>
          </div>
        )}
      </div>
    </div>
  )
}
