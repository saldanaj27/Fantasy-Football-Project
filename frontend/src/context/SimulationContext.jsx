import { createContext, useContext, useState, useEffect } from 'react'
import { setSimulationParams } from '../api/client'

const SimulationContext = createContext()

// eslint-disable-next-line react-refresh/only-export-components
export function useSimulation() {
  const context = useContext(SimulationContext)
  if (!context) {
    throw new Error('useSimulation must be used within a SimulationProvider')
  }
  return context
}

export function SimulationProvider({ children }) {
  const [simulation, setSimulation] = useState(() => {
    const saved = localStorage.getItem('statstack-simulation')
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch {
        return { active: false, season: null, week: null }
      }
    }
    return { active: false, season: null, week: null }
  })

  // Sync simulation state to Axios interceptor
  useEffect(() => {
    if (simulation.active) {
      setSimulationParams({ season: simulation.season, week: simulation.week })
    } else {
      setSimulationParams(null)
    }
    localStorage.setItem('statstack-simulation', JSON.stringify(simulation))
  }, [simulation])

  const startSimulation = (season, week) => {
    setSimulation({ active: true, season, week })
  }

  const stopSimulation = () => {
    setSimulation({ active: false, season: null, week: null })
  }

  const updateWeek = (week) => {
    setSimulation((prev) => ({ ...prev, week }))
  }

  return (
    <SimulationContext.Provider
      value={{ simulation, startSimulation, stopSimulation, updateWeek }}
    >
      {children}
    </SimulationContext.Provider>
  )
}
