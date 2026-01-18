import { useEffect, useState } from "react"
import { getDefenseAllowed, getRecentStats } from '../../../api/analytics'
import StatCard from "./StatCard"
import PositionStatCard from "./PositionStatCard"
import "../css/TeamStatsSection.css"

export default function TeamStatsSection({ team, numGames }) {
  const [teamStats, setTeamStats] = useState(null)
  const [rbStats, setRbStats] = useState(null)
  const [wrStats, setWrStats] = useState(null)

  useEffect(() => {
    const fetchTeamData = async () => {
      const data = await getRecentStats(numGames, team.id)
      setTeamStats(data)
    }

    const fetchDefenseData = async () => {
      const [rbData, wrData] = await Promise.all([
        getDefenseAllowed(numGames, team.id, 'RB'),
        getDefenseAllowed(numGames, team.id, 'WR')
      ])
      setRbStats(rbData)
      setWrStats(wrData)
    }

    fetchDefenseData()
    fetchTeamData()
  }, [numGames, team.id])

  if (!teamStats || !rbStats || !wrStats) {
    return (
      <div className="loading-container">
        <div className="loading-text">Loading...</div>
      </div>
    )
  }

  return (
    <div className="team-stats-section">
      <div className="team-header">
        <h3>{team.abbreviation}</h3>
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
            value={teamStats.points_per_game}
          />
          <StatCard 
            title="Total Yards/Game" 
            value={teamStats.total_yards_per_game}
          />
          <StatCard 
            title="Pass Yards/Game" 
            value={teamStats.passing.total_yards_average.toFixed(1)}
            subtitle={`${(teamStats.passing.completion_percentage * 100).toFixed(1)}% comp`}
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
      </div>

      {/* Defense vs Position Stat */}
      <div className="defense-stats">
        <h4 className="section-title">
          <span className="section-title-bar defense"></span>
          Defense vs Position (Last {numGames} Games)
        </h4>
        <PositionStatCard position="RB" stats={rbStats} numGames={numGames} />
        <PositionStatCard position="WR" stats={wrStats} numGames={numGames} />
      </div>
    </div>
  )
}