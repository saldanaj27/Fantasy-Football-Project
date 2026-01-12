import { useEffect, useState } from "react"
import { getRecentStats } from '../api/analytics'
import StatCard from "./StatCard"

export default function TeamStatsSection({ team, numGames }) {
  const [teamStats, setTeamStats] = useState(null)

  useEffect(() => {
    const fetchTeamData = async () => {
      const data = await getRecentStats(numGames, team.id)
      setTeamStats(data)
    }
    fetchTeamData()
  }, [])

  return (
    <div>
      <div>
        <h3>{team.abbreviation}</h3>
        <p>{team.name}</p>
      </div>

      {/* Offensive Team Stats */}
      <div>
        <h4>Offensive Stats (Last {numGames} Games)</h4>
        <div>
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
    </div>
  )
}