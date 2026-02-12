import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()

// eslint-disable-next-line react-refresh/only-export-components
export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

function getTimeBasedTheme() {
  const hour = new Date().getHours()
  // Light mode: 6 AM - 6 PM (hours 6-17)
  // Dark mode: 6 PM - 6 AM (hours 18-5)
  return hour >= 6 && hour < 18 ? 'light' : 'dark'
}

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    // Check localStorage for user preference
    const savedTheme = localStorage.getItem('statstack-theme')
    if (savedTheme) {
      return savedTheme
    }
    // Otherwise use time-based theme
    return getTimeBasedTheme()
  })

  const [isAutoMode, setIsAutoMode] = useState(() => {
    return localStorage.getItem('statstack-theme-auto') !== 'false'
  })

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  // Auto-update theme based on time when in auto mode
  useEffect(() => {
    if (!isAutoMode) return

    const checkTime = () => {
      const newTheme = getTimeBasedTheme()
      if (newTheme !== theme) {
        setTheme(newTheme)
      }
    }

    // Check every minute
    const interval = setInterval(checkTime, 60000)
    return () => clearInterval(interval)
  }, [isAutoMode, theme])

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    setIsAutoMode(false)
    localStorage.setItem('statstack-theme', newTheme)
    localStorage.setItem('statstack-theme-auto', 'false')
  }

  const enableAutoMode = () => {
    setIsAutoMode(true)
    localStorage.removeItem('statstack-theme')
    localStorage.setItem('statstack-theme-auto', 'true')
    setTheme(getTimeBasedTheme())
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, isAutoMode, enableAutoMode }}>
      {children}
    </ThemeContext.Provider>
  )
}
