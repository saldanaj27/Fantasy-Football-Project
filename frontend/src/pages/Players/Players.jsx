import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { searchPlayers, getTeams } from '../../api/players'
import PlayerCard from './components/PlayerCard'
import './styles/Players.css'

export default function Players() {
  const [players, setPlayers] = useState([])
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [position, setPosition] = useState('')
  const [team, setTeam] = useState('')

  // Debounce search
  const [debouncedSearch, setDebouncedSearch] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search)
    }, 300)
    return () => clearTimeout(timer)
  }, [search])

  // Load teams for filter dropdown
  useEffect(() => {
    const loadTeams = async () => {
      try {
        const data = await getTeams()
        // Sort teams alphabetically
        const sortedTeams = [...data].sort((a, b) =>
          a.abbreviation.localeCompare(b.abbreviation)
        )
        setTeams(sortedTeams)
      } catch (error) {
        console.error('Error loading teams:', error)
      }
    }
    loadTeams()
  }, [])

  // Search players
  const fetchPlayers = useCallback(async () => {
    setLoading(true)
    try {
      const data = await searchPlayers({
        search: debouncedSearch,
        position: position || undefined,
        team: team || undefined,
        limit: 100
      })
      setPlayers(data.players)
    } catch (error) {
      console.error('Error searching players:', error)
      setPlayers([])
    } finally {
      setLoading(false)
    }
  }, [debouncedSearch, position, team])

  useEffect(() => {
    fetchPlayers()
  }, [fetchPlayers])

  return (
    <div className="players-page">
      {/* Top Navigation */}
      <nav className="top-nav">
        <Link to="/" className="brand">FANTASY FOOTBALL</Link>
        <div className="nav-links">
          <Link to="/" className="nav-link">Scores</Link>
          <Link to="/players" className="nav-link active">Players</Link>
        </div>
      </nav>

      <div className="players-content">
        <h1 className="page-title">Player Search</h1>

        {/* Search and Filters */}
        <div className="search-filters">
          <div className="search-row">
            <div className="search-input-wrapper">
              <input
                type="text"
                className="search-input"
                placeholder="Search players by name..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <select
              className="filter-select"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
            >
              <option value="">All Positions</option>
              <option value="QB">QB</option>
              <option value="RB">RB</option>
              <option value="WR">WR</option>
              <option value="TE">TE</option>
            </select>

            <select
              className="filter-select"
              value={team}
              onChange={(e) => setTeam(e.target.value)}
            >
              <option value="">All Teams</option>
              {teams.map((t) => (
                <option key={t.id} value={t.abbreviation}>
                  {t.abbreviation} - {t.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Results Info */}
        <div className="results-info">
          <span className="results-count">
            {loading ? 'Searching...' : `${players.length} players found`}
          </span>
        </div>

        {/* Players Grid */}
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
          </div>
        ) : players.length > 0 ? (
          <div className="players-grid">
            {players.map((player) => (
              <PlayerCard key={player.id} player={player} />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">🏈</div>
            <div className="empty-state-text">No players found</div>
            <div className="empty-state-subtext">
              Try adjusting your search or filters
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
