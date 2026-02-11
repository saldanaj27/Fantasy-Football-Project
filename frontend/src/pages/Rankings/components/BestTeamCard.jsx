import { useEffect, useState } from 'react'
import { getBestTeam } from '../../../api/analytics'
import './BestTeamCard.css'

const SLOT_LABELS = [
  { key: 'QB', label: 'QB', count: 1 },
  { key: 'RB', label: 'RB', count: 2 },
  { key: 'WR', label: 'WR', count: 2 },
  { key: 'TE', label: 'TE', count: 1 },
  { key: 'FLEX', label: 'FLEX', count: 1 },
]

export default function BestTeamCard({ numGames }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const result = await getBestTeam(numGames)
        setData(result)
      } catch (error) {
        console.error('Error fetching best team:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [numGames])

  if (loading) return <div className="best-team-loading">Loading optimal roster...</div>
  if (!data) return null

  return (
    <div className="best-team-card">
      <div className="best-team-header">
        <h3 className="best-team-title">Optimal Fantasy Roster</h3>
        <div className="best-team-total">
          <span className="total-label">Proj. Weekly</span>
          <span className="total-value">{data.projected_weekly_total} pts</span>
        </div>
      </div>
      <div className="best-team-roster">
        {SLOT_LABELS.map(slot => (
          data.roster[slot.key]?.map((player, i) => (
            <div key={`${slot.key}-${i}`} className="roster-slot">
              <span className={`slot-label ${slot.key.toLowerCase()}`}>{slot.label}</span>
              <div className="slot-player">
                {player.image_url && (
                  <img src={player.image_url} alt={player.name} className="slot-image" onError={(e) => { e.target.style.display = 'none' }} />
                )}
                <div className="slot-info">
                  <span className="slot-name">{player.name}</span>
                  <span className="slot-team">{player.team}</span>
                </div>
              </div>
              <span className="slot-fpts">{player.avg_fpts}</span>
            </div>
          ))
        ))}
      </div>
    </div>
  )
}
