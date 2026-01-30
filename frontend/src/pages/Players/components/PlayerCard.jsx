import "../styles/PlayerCard.css"

export default function PlayerCard({ player }) {
  const { name, position, team, image_url, stats } = player

  // Get initials for placeholder
  const getInitials = (name) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  // Render position-specific stats
  const renderStats = () => {
    if (position === 'QB') {
      return (
        <div className="player-stats-row">
          <div className="stat-item">
            <div className="stat-value">{stats.avg_pass_yards.toFixed(1)}</div>
            <div className="stat-label">Pass Yds</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.avg_rush_yards.toFixed(1)}</div>
            <div className="stat-label">Rush Yds</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.games_played}</div>
            <div className="stat-label">Games</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.total_fantasy_points.toFixed(1)}</div>
            <div className="stat-label">Total Pts</div>
          </div>
        </div>
      )
    }

    if (position === 'RB') {
      return (
        <div className="player-stats-row">
          <div className="stat-item">
            <div className="stat-value">{stats.avg_rush_attempts.toFixed(1)}</div>
            <div className="stat-label">Carries</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.avg_rush_yards.toFixed(1)}</div>
            <div className="stat-label">Rush Yds</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.avg_targets.toFixed(1)}</div>
            <div className="stat-label">Targets</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.games_played}</div>
            <div className="stat-label">Games</div>
          </div>
        </div>
      )
    }

    // WR and TE
    return (
      <div className="player-stats-row">
        <div className="stat-item">
          <div className="stat-value">{stats.avg_targets.toFixed(1)}</div>
          <div className="stat-label">Targets</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">{stats.avg_receptions.toFixed(1)}</div>
          <div className="stat-label">Rec</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">{stats.avg_receiving_yards.toFixed(1)}</div>
          <div className="stat-label">Rec Yds</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">{stats.games_played}</div>
          <div className="stat-label">Games</div>
        </div>
      </div>
    )
  }

  return (
    <div className="player-card">
      <div className="player-card-header">
        {image_url ? (
          <img
            src={image_url}
            alt={name}
            className="player-image"
            onError={(e) => {
              e.target.style.display = 'none'
              e.target.nextSibling.style.display = 'flex'
            }}
          />
        ) : null}
        <div
          className="player-image-placeholder"
          style={{ display: image_url ? 'none' : 'flex' }}
        >
          {getInitials(name)}
        </div>

        <div className="player-info">
          <h3 className="player-name">{name}</h3>
          <div className="player-meta">
            <span className={`position-badge ${position.toLowerCase()}`}>
              {position}
            </span>
            <span>{team}</span>
          </div>
        </div>

        <div className="fantasy-points-badge">
          <span>{stats.avg_fantasy_points.toFixed(1)}</span>
          <span className="fantasy-points-label">PPR/G</span>
        </div>
      </div>

      {renderStats()}
    </div>
  )
}
