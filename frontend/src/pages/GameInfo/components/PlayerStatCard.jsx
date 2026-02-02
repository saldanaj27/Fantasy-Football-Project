import "../styles/PlayerStatCard.css"

export default function PlayerStatCard({ player, position }) {
  const renderQBStats = () => (
    <div className="player-stats-grid qb">
      <div className="stat-item">
        <span className="stat-label">Pass Yds</span>
        <span className="stat-value">{player.stats.pass_yards.toFixed(1)}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Pass TDs</span>
        <span className="stat-value">{player.stats.pass_touchdowns.toFixed(1)}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">INTs</span>
        <span className="stat-value">{player.stats.interceptions.toFixed(1)}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Rush Yds</span>
        <span className="stat-value">{player.stats.rush_yards.toFixed(1)}</span>
      </div>
      {player.stats.snap_pct > 0 && (
        <div className="stat-item advanced">
          <span className="stat-label">Snap %</span>
          <span className="stat-value">{player.stats.snap_pct.toFixed(0)}%</span>
        </div>
      )}
    </div>
  )

  const renderRBStats = () => (
    <div className="player-stats-grid rb">
      <div className="stat-item">
        <span className="stat-label">Carries</span>
        <span className="stat-value">{player.stats.rush_attempts.toFixed(1)}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Rush Yds</span>
        <span className="stat-value">{player.stats.rush_yards.toFixed(1)}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Rush TDs</span>
        <span className="stat-value">{player.stats.rush_touchdowns.toFixed(1)}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Targets</span>
        <span className="stat-value">{player.stats.targets.toFixed(1)}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Rec Yds</span>
        <span className="stat-value">{player.stats.receiving_yards.toFixed(1)}</span>
      </div>
      {player.stats.snap_pct > 0 && (
        <div className="stat-item advanced">
          <span className="stat-label">Snap %</span>
          <span className="stat-value">{player.stats.snap_pct.toFixed(0)}%</span>
        </div>
      )}
    </div>
  )

  const renderWRTEStats = () => (
    <div className="player-stats-grid wr-te">
      <div className="stat-item">
        <span className="stat-label">Targets</span>
        <span className="stat-value">{player.stats.targets.toFixed(1)}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Receptions</span>
        <span className="stat-value">{player.stats.receptions.toFixed(1)}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Rec Yds</span>
        <span className="stat-value">{player.stats.receiving_yards.toFixed(1)}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Rec TDs</span>
        <span className="stat-value">{player.stats.receiving_touchdowns.toFixed(1)}</span>
      </div>
      {player.stats.adot > 0 && (
        <div className="stat-item advanced">
          <span className="stat-label">aDOT</span>
          <span className="stat-value">{player.stats.adot.toFixed(1)}</span>
        </div>
      )}
      {player.stats.yards_after_catch > 0 && (
        <div className="stat-item advanced">
          <span className="stat-label">YAC</span>
          <span className="stat-value">{player.stats.yards_after_catch.toFixed(1)}</span>
        </div>
      )}
      {player.stats.snap_pct > 0 && (
        <div className="stat-item advanced">
          <span className="stat-label">Snap %</span>
          <span className="stat-value">{player.stats.snap_pct.toFixed(0)}%</span>
        </div>
      )}
    </div>
  )

  return (
    <div className="player-stat-card">
      <div className="player-header">
        <span className={`position-badge ${position.toLowerCase()}`}>
          {position}
        </span>
        <span className="player-name">{player.name}</span>
        <span className="games-played">{player.games_played}G</span>
      </div>

      {position === 'QB' && renderQBStats()}
      {position === 'RB' && renderRBStats()}
      {(position === 'WR' || position === 'TE') && renderWRTEStats()}

      <div className="fantasy-points-row">
        <span className="fantasy-label">Fantasy PPR</span>
        <span className="fantasy-value">{player.stats.fantasy_points_ppr.toFixed(1)}</span>
      </div>
    </div>
  )
}
