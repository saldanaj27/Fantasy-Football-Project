import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { searchPlayers } from '../../api/players'
import './styles/Rankings.css'

const POSITIONS = ['ALL', 'QB', 'RB', 'WR', 'TE']
const PAGE_SIZE = 25

export default function Rankings() {
  const [players, setPlayers] = useState([])
  const [loading, setLoading] = useState(true)
  const [position, setPosition] = useState('ALL')
  const [numGames, setNumGames] = useState(3)
  const [sortConfig, setSortConfig] = useState({ key: 'avg_fantasy_points', direction: 'desc' })
  const [currentPage, setCurrentPage] = useState(1)

  // Fetch players
  useEffect(() => {
    const fetchPlayers = async () => {
      setLoading(true)
      try {
        const data = await searchPlayers({
          position: position === 'ALL' ? undefined : position,
          games: numGames,
          limit: 200
        })
        setPlayers(data.players)
        setCurrentPage(1)
      } catch (error) {
        console.error('Error fetching rankings:', error)
        setPlayers([])
      } finally {
        setLoading(false)
      }
    }
    fetchPlayers()
  }, [position, numGames])

  // Sort players
  const sortedPlayers = useMemo(() => {
    const sorted = [...players]
    sorted.sort((a, b) => {
      let aVal, bVal

      if (sortConfig.key === 'name') {
        aVal = a.name
        bVal = b.name
        return sortConfig.direction === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal)
      }

      // Stats are nested
      if (sortConfig.key.startsWith('stats.')) {
        const statKey = sortConfig.key.replace('stats.', '')
        aVal = a.stats[statKey] || 0
        bVal = b.stats[statKey] || 0
      } else {
        aVal = a.stats[sortConfig.key] || 0
        bVal = b.stats[sortConfig.key] || 0
      }

      return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal
    })
    return sorted
  }, [players, sortConfig])

  // Paginate
  const paginatedPlayers = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE
    return sortedPlayers.slice(start, start + PAGE_SIZE)
  }, [sortedPlayers, currentPage])

  const totalPages = Math.ceil(sortedPlayers.length / PAGE_SIZE)

  // Handle sort
  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'desc' ? 'asc' : 'desc'
    }))
  }

  // Get sort icon
  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return ''
    return sortConfig.direction === 'desc' ? '▼' : '▲'
  }

  // Get initials for placeholder
  const getInitials = (name) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  // Define columns based on position filter
  const getColumns = () => {
    const baseColumns = [
      { key: 'rank', label: 'RK', sortable: false },
      { key: 'name', label: 'Player', sortable: true },
      { key: 'avg_fantasy_points', label: 'FPTS/G', sortable: true },
      { key: 'total_fantasy_points', label: 'Total', sortable: true },
      { key: 'games_played', label: 'GP', sortable: true },
    ]

    if (position === 'QB' || position === 'ALL') {
      baseColumns.push({ key: 'avg_pass_yards', label: 'Pass YDS', sortable: true })
    }
    if (position !== 'QB') {
      baseColumns.push(
        { key: 'avg_targets', label: 'TGT', sortable: true },
        { key: 'avg_receptions', label: 'REC', sortable: true },
        { key: 'avg_receiving_yards', label: 'REC YDS', sortable: true },
      )
    }
    if (position === 'RB' || position === 'ALL') {
      baseColumns.push(
        { key: 'avg_rush_attempts', label: 'CAR', sortable: true },
        { key: 'avg_rush_yards', label: 'Rush YDS', sortable: true },
      )
    }

    return baseColumns
  }

  const columns = getColumns()

  return (
    <div className="rankings-page">
      {/* Top Navigation */}
      <nav className="top-nav">
        <Link to="/" className="brand">FANTASY FOOTBALL</Link>
        <div className="nav-links">
          <Link to="/" className="nav-link">Scores</Link>
          <Link to="/players" className="nav-link">Players</Link>
          <Link to="/rankings" className="nav-link">Rankings</Link>
          <Link to="/start-sit" className="nav-link">Start/Sit</Link>
        </div>
      </nav>

      <div className="rankings-content">
        <h1 className="page-title">Fantasy Rankings</h1>

        {/* Filters */}
        <div className="filters-bar">
          <div className="position-filters">
            {POSITIONS.map(pos => (
              <button
                key={pos}
                className={`position-btn ${position === pos ? 'active' : ''}`}
                onClick={() => setPosition(pos)}
              >
                {pos}
              </button>
            ))}
          </div>

          <div className="games-filter">
            <label>Last</label>
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
        </div>

        {/* Rankings Table */}
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
          </div>
        ) : (
          <div className="rankings-table-container">
            <table className="rankings-table">
              <thead>
                <tr>
                  {columns.map(col => (
                    <th
                      key={col.key}
                      className={`${col.sortable ? 'sortable' : ''} ${sortConfig.key === col.key ? 'sorted' : ''}`}
                      onClick={() => col.sortable && handleSort(col.key)}
                    >
                      {col.label}
                      {col.sortable && <span className="sort-icon">{getSortIcon(col.key)}</span>}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {paginatedPlayers.map((player, index) => (
                  <tr key={player.id}>
                    <td className="rank-cell">
                      {(currentPage - 1) * PAGE_SIZE + index + 1}
                    </td>
                    <td>
                      <div className="player-cell">
                        {player.image_url ? (
                          <img
                            src={player.image_url}
                            alt={player.name}
                            className="player-image"
                            onError={(e) => {
                              e.target.style.display = 'none'
                              e.target.nextSibling.style.display = 'flex'
                            }}
                          />
                        ) : null}
                        <div
                          className="player-image-placeholder"
                          style={{ display: player.image_url ? 'none' : 'flex' }}
                        >
                          {getInitials(player.name)}
                        </div>
                        <div className="player-info">
                          <span className="player-name">{player.name}</span>
                          <span className="player-team">
                            <span className={`position-badge ${player.position.toLowerCase()}`}>
                              {player.position}
                            </span>
                            {' '}{player.team}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="fpts-cell">{player.stats.avg_fantasy_points.toFixed(1)}</td>
                    <td className="stat-cell">{player.stats.total_fantasy_points.toFixed(1)}</td>
                    <td className="stat-cell">{player.stats.games_played}</td>
                    {(position === 'QB' || position === 'ALL') && (
                      <td className="stat-cell">{player.stats.avg_pass_yards.toFixed(1)}</td>
                    )}
                    {position !== 'QB' && (
                      <>
                        <td className="stat-cell">{player.stats.avg_targets.toFixed(1)}</td>
                        <td className="stat-cell">{player.stats.avg_receptions.toFixed(1)}</td>
                        <td className="stat-cell">{player.stats.avg_receiving_yards.toFixed(1)}</td>
                      </>
                    )}
                    {(position === 'RB' || position === 'ALL') && (
                      <>
                        <td className="stat-cell">{player.stats.avg_rush_attempts.toFixed(1)}</td>
                        <td className="stat-cell">{player.stats.avg_rush_yards.toFixed(1)}</td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            <div className="pagination">
              <div className="pagination-info">
                Showing {(currentPage - 1) * PAGE_SIZE + 1}-{Math.min(currentPage * PAGE_SIZE, sortedPlayers.length)} of {sortedPlayers.length}
              </div>
              <div className="pagination-buttons">
                <button
                  className="pagination-btn"
                  onClick={() => setCurrentPage(p => p - 1)}
                  disabled={currentPage === 1}
                >
                  Previous
                </button>
                <button
                  className="pagination-btn"
                  onClick={() => setCurrentPage(p => p + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
