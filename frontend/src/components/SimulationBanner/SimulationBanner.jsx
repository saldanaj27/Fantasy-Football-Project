import { useState } from 'react'
import { useSimulation } from '../../context/SimulationContext'
import './SimulationBanner.css'

const SEASONS = [2020, 2021, 2022, 2023, 2024]
const WEEKS = Array.from({ length: 18 }, (_, i) => i + 1)

export default function SimulationBanner() {
  const { simulation, startSimulation, stopSimulation, updateWeek } = useSimulation()
  const [showSetup, setShowSetup] = useState(false)
  const [setupSeason, setSetupSeason] = useState(2024)
  const [setupWeek, setSetupWeek] = useState(5)

  // Active simulation banner
  if (simulation.active) {
    const canPrev = simulation.week > 1
    const canNext = simulation.week < 18

    return (
      <div className="simulation-banner active">
        <div className="simulation-banner-content">
          <span className="simulation-label">Time Travel Mode</span>
          <div className="simulation-controls">
            <button
              className="sim-btn"
              disabled={!canPrev}
              onClick={() => updateWeek(simulation.week - 1)}
            >
              Prev
            </button>
            <span className="simulation-week">
              {simulation.season} &middot; Week {simulation.week}
            </span>
            <button
              className="sim-btn"
              disabled={!canNext}
              onClick={() => updateWeek(simulation.week + 1)}
            >
              Next
            </button>
          </div>
          <button className="sim-btn exit" onClick={stopSimulation}>
            Exit
          </button>
        </div>
      </div>
    )
  }

  // Setup form
  if (showSetup) {
    return (
      <div className="simulation-banner setup">
        <div className="simulation-banner-content">
          <span className="simulation-label">Start Time Travel</span>
          <div className="simulation-setup-fields">
            <select
              value={setupSeason}
              onChange={(e) => setSetupSeason(Number(e.target.value))}
            >
              {SEASONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <select
              value={setupWeek}
              onChange={(e) => setSetupWeek(Number(e.target.value))}
            >
              {WEEKS.map((w) => (
                <option key={w} value={w}>Week {w}</option>
              ))}
            </select>
          </div>
          <div className="simulation-setup-actions">
            <button
              className="sim-btn go"
              onClick={() => {
                startSimulation(setupSeason, setupWeek)
                setShowSetup(false)
              }}
            >
              Go
            </button>
            <button className="sim-btn" onClick={() => setShowSetup(false)}>
              Cancel
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Inactive toggle
  return (
    <div className="simulation-banner inactive">
      <button className="sim-toggle-btn" onClick={() => setShowSetup(true)}>
        Time Travel
      </button>
    </div>
  )
}
