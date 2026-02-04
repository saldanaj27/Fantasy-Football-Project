import { useEffect, useState } from "react"
import { getDefenseAllowed, getRecentStats } from '../../../api/analytics'
import StatCard from "./StatCard"
import PositionStatCard from "./PositionStatCard"
import "../styles/TeamStatsSection.css"

export default function TeamStatsSection({ team, numGames }) {
  const [teamStats, setTeamStats] = useState(null)
  const [rbStats, setRbStats] = useState(null)
  const [wrStats, setWrStats] = useState(null)
  const [teStats, setTeStats] = useState(null)
  const [qbStats, setQbStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true)
      try {
        // Fetch all stats in parallel
        const [teamData, rbData, wrData, teData, qbData] = await Promise.all([
          getRecentStats(numGames, team.id),
          getDefenseAllowed(numGames, team.id, 'RB'),
          getDefenseAllowed(numGames, team.id, 'WR'),
          getDefenseAllowed(numGames, team.id, 'TE'),
          getDefenseAllowed(numGames, team.id, 'QB')
        ])
        
        setTeamStats(teamData)
        setRbStats(rbData)
        setWrStats(wrData)
        setTeStats(teData)
        setQbStats(qbData)
      } catch (error) {
        console.error('Error fetching team data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchAllData()
  }, [numGames, team.id])

  if (loading || !teamStats || !rbStats || !wrStats || !teStats || !qbStats) {
    return (
      <div className="loading-container">
        <div className="loading-text">Loading...</div>
      </div>
    )
  }

  const turnoverDiff = teamStats.def_turnovers_total - teamStats.off_turnovers_total

  return (
    <div className="team-stats-section">
      <div className="team-header">
        <h3>{team.abbreviation} <span className="team-record">({team.record})</span></h3>
        <p>{team.name}</p>
      </div>

      {/* Offensive Team Stats */}
      <div className="offensive-stats">
        <h4 className="section-title">
          <span className="section-title-bar"></span>
          Offensive Stats (Last {numGames} Games)
        </h4>
        <div className="stats-grid">
          <StatCard 
            title="Points/Game" 
            value={teamStats.points_per_game.toFixed(1)}
          />
          <StatCard 
            title="Total Yards/Game" 
            value={teamStats.total_yards_per_game.toFixed(0)}
          />
          <StatCard 
            title="Pass Yards/Game" 
            value={teamStats.passing.total_yards_average.toFixed(1)}
            subtitle={`${(teamStats.passing.completion_percentage).toFixed(1)}% comp`}
          />
          <StatCard 
            title="Rush Yards/Game" 
            value={teamStats.rushing.total_yards_average.toFixed(1)}
          />
          <StatCard 
            title="Pass TDs/Game" 
            value={teamStats.passing.touchdowns.toFixed(1)}
          />
          <StatCard 
            title="Rush TDs/Game" 
            value={teamStats.rushing.touchdowns.toFixed(1)}
          />
        </div>

        <div className="turnover-differential">
          <div className="turnover-differential-content">
            <span className="turnover-differential-label">Turnover Differential</span>
            <span className={`turnover-differential-value ${turnoverDiff > 0 ? 'positive' : 'negative'}`}>
              {turnoverDiff > 0 ? '+' : ''}{turnoverDiff}
            </span>
          </div>
          <div className="turnover-differential-details">
            {teamStats.def_turnovers_total} forced • {teamStats.off_turnovers_total} committed
          </div>
        </div>
      </div>

      {/* Defense vs Position Stats */}
      <div className="defense-stats">
        <h4 className="section-title">
          <span className="section-title-bar defense"></span>
          Defense vs Position (Last {numGames} Games)
        </h4>
        
        <PositionStatCard position="QB" stats={qbStats} numGames={numGames} />
        <PositionStatCard position="RB" stats={rbStats} numGames={numGames} />
        <PositionStatCard position="WR" stats={wrStats} numGames={numGames} />
        <PositionStatCard position="TE" stats={teStats} numGames={numGames} />
      </div>
    </div>
  )
}