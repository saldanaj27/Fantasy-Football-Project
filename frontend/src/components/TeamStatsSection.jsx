import { useEffect, useState } from "react"
import { getRecentStats } from '../api/analytics'

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

            <div>
                <h4>Offensive Stats (Last {numGames} Games)</h4>
            </div>
        </div>
    )
}