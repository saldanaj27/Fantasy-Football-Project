import "../styles/PositionStatCard.css"

export default function PositionStatCard({ position, stats }) {
  // Helper function to get position display name
  const getPositionName = (pos) => {
    const names = {
      'RB': 'Running Backs',
      'WR': 'Wide Receivers',
      'TE': 'Tight Ends',
      'QB': 'Quarterbacks'
    }
    return names[pos] || pos
  }

  // Render for QB position (has passing stats)
  if (position === 'QB') {
    return (
      <div className="position-stat-card">
        <div className="position-stat-header">
          <span className={`position-badge ${position.toLowerCase()}`}>
            {position}
          </span>
          vs {getPositionName(position)}
        </div>
        
        {/* Passing Stats Grid */}
        <div className="position-stats-grid qb-grid">
          <div>
            <div className="position-stat-item-label">Pass Yds/G</div>
            <div className="position-stat-item-value">
              {stats.passing.yards.toFixed(1)}
            </div>
          </div>
          <div>
            <div className="position-stat-item-label">Pass TDs/G</div>
            <div className="position-stat-item-value">
              {stats.passing.touchdowns.toFixed(1)}
            </div>
          </div>
          <div>
            <div className="position-stat-item-label">INTs/G</div>
            <div className="position-stat-item-value">
              {stats.passing.interceptions.toFixed(1)}
            </div>
          </div>
          <div>
            <div className="position-stat-item-label">Comp %</div>
            <div className="position-stat-item-value">
              {stats.passing.completion_percentage.toFixed(1)}%
            </div>
          </div>
          <div>
            <div className="position-stat-item-label">Rush Yds/G</div>
            <div className="position-stat-item-value">
              {stats.rushing.yards.toFixed(1)}
            </div>
          </div>
          <div>
            <div className="position-stat-item-label">Sacks/G</div>
            <div className="position-stat-item-value">
              {stats.passing.sacks.toFixed(1)}
            </div>
          </div>
        </div>
        
        <div className="position-fantasy-points">
          Fantasy Pts/G: <span>{stats.fantasy_points.toFixed(1)}</span>
          <span className="total-yards-separator">•</span>
          Total Yds/G: <span>{stats.total_yards_allowed.toFixed(1)}</span>
        </div>
      </div>
    )
  }

  // Render for RB, WR, TE (have rushing/receiving stats)
  return (
    <div className="position-stat-card">
      <div className="position-stat-header">
        <span className={`position-badge ${position.toLowerCase()}`}>
          {position}
        </span>
        vs {getPositionName(position)}
      </div>
      
      <div className="position-stats-grid">
        <div>
          <div className="position-stat-item-label">
            {position === 'RB' ? 'Rush Yds/G' : position === 'TE' ? 'Rec Yds/G' : 'Targets/G'}
          </div>
          <div className="position-stat-item-value">
            {position === 'RB' 
              ? stats.rushing.yards.toFixed(1)
              : position === 'TE'
                ? stats.receiving.yards.toFixed(1)
                : stats.receiving.targets.toFixed(1)
            }
          </div>
        </div>
        <div>
          <div className="position-stat-item-label">
            {position === 'RB' ? 'Rec Yds/G' : 'Receptions/G'}
          </div>
          <div className="position-stat-item-value">
            {position === 'RB' 
              ? stats.receiving.yards.toFixed(1)
              : stats.receiving.receptions.toFixed(1)
            }
          </div>
        </div>
        <div>
          <div className="position-stat-item-label">Total Yds/G</div>
          <div className="position-stat-item-value">
            {stats.total_yards_allowed.toFixed(1)}
          </div>
        </div>
      </div>
      
      {/* Show rushing and receiving touchdowns for RB/WR/TE */}
      <div className="position-touchdowns">
        <div>
          <span className="td-label">Rush TDs/G:</span>
          <span className="td-value">{stats.rushing.touchdowns.toFixed(1)}</span>
        </div>
        <div>
          <span className="td-label">Rec TDs/G:</span>
          <span className="td-value">{stats.receiving.touchdowns.toFixed(1)}</span>
        </div>
      </div>
      
      <div className="position-fantasy-points">
        Fantasy Pts/G: <span>{stats.fantasy_points.toFixed(1)}</span>
      </div>
    </div>
  )
}