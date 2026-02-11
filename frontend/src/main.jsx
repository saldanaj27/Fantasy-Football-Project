import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ThemeProvider } from './context/ThemeContext'
import { SimulationProvider } from './context/SimulationContext'
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary'
import App from './App.jsx'
import './styles/theme.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider>
      <SimulationProvider>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      </SimulationProvider>
    </ThemeProvider>
  </StrictMode>,
)
