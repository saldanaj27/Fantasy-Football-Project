import "../css/PositionStatCard.css"

export default function PositionStatCard({ position, stats, numGames }) {
  return (
    <div className="position-stat-card">
      <div className="position-stat-header">
        <span className={`position-badge ${position.toLowerCase()}`}>
          {position}
        </span>
        vs {position === 'RB' ? 'Running Backs' : 'Wide Receivers'}
      </div>
      
      <div className="position-stats-grid">
        <div>
          <div className="position-stat-item-label">
            {position === 'RB' ? 'Rush Yds/G' : 'Targets/G'}
          </div>
          <div className="position-stat-item-value">
            {position === 'RB' 
              ? stats.rushing.yards.toFixed(1)
              : stats.receiving.targets.toFixed(1)
            }
          </div>
        </div>
        <div>
          <div className="position-stat-item-label">Rec Yds/G</div>
          <div className="position-stat-item-value">
            {stats.receiving.yards.toFixed(1)}
          </div>
        </div>
        <div>
          <div className="position-stat-item-label">Total Yds/G</div>
          <div className="position-stat-item-value">
            {stats.total_yards_allowed.toFixed(1)}
          </div>
        </div>
      </div>
      
      <div className="position-fantasy-points">
        Fantasy Pts/G: <span>{stats.fantasy_points.toFixed(1)}</span>
      </div>
    </div>
  )
}