import { useState } from 'react'

export default function DraftSetup({ onStart }) {
  const [numTeams, setNumTeams] = useState(10)
  const [numRounds, setNumRounds] = useState(15)
  const [userPosition, setUserPosition] = useState(1)
  const [scoringFormat, setScoringFormat] = useState('PPR')
  const [loading, setLoading] = useState(false)

  const handleStart = async () => {
    setLoading(true)
    try {
      await onStart({
        num_teams: numTeams,
        num_rounds: numRounds,
        user_team_position: userPosition,
        scoring_format: scoringFormat,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="draft-setup">
      <h1 className="draft-setup-title">Mock Draft Setup</h1>
      <p className="draft-setup-subtitle">Configure your draft and compete against AI opponents</p>

      <div className="setup-form">
        <div className="setup-field">
          <label>Number of Teams</label>
          <select value={numTeams} onChange={(e) => setNumTeams(Number(e.target.value))}>
            {[8, 10, 12, 14].map(n => (
              <option key={n} value={n}>{n} Teams</option>
            ))}
          </select>
        </div>

        <div className="setup-field">
          <label>Rounds</label>
          <select value={numRounds} onChange={(e) => setNumRounds(Number(e.target.value))}>
            {[13, 15, 16, 18].map(n => (
              <option key={n} value={n}>{n} Rounds</option>
            ))}
          </select>
        </div>

        <div className="setup-field">
          <label>Your Draft Position</label>
          <select value={userPosition} onChange={(e) => setUserPosition(Number(e.target.value))}>
            {Array.from({ length: numTeams }, (_, i) => i + 1).map(n => (
              <option key={n} value={n}>Pick #{n}</option>
            ))}
          </select>
        </div>

        <div className="setup-field">
          <label>Scoring Format</label>
          <select value={scoringFormat} onChange={(e) => setScoringFormat(e.target.value)}>
            <option value="PPR">PPR</option>
            <option value="HALF">Half PPR</option>
            <option value="STD">Standard</option>
          </select>
        </div>

        <button className="start-draft-btn" onClick={handleStart} disabled={loading}>
          {loading ? 'Starting Draft...' : 'Start Draft'}
        </button>
      </div>
    </div>
  )
}
