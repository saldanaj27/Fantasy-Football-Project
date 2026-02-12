import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import GameBox from './GameBox'
import { renderWithRouter, mockGame, mockUpcomingGame } from '../../../test/testUtils'

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('GameBox', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
  })

  describe('Finished Game', () => {
    it('renders team abbreviations', () => {
      renderWithRouter(<GameBox game={mockGame} />)

      // TeamLogo fallback also renders abbreviation, so use getAllByText
      expect(screen.getAllByText('KC').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('SF').length).toBeGreaterThanOrEqual(1)
    })

    it('renders team names', () => {
      renderWithRouter(<GameBox game={mockGame} />)

      expect(screen.getByText('Kansas City Chiefs')).toBeInTheDocument()
      expect(screen.getByText('San Francisco 49ers')).toBeInTheDocument()
    })

    it('renders final scores', () => {
      renderWithRouter(<GameBox game={mockGame} />)

      expect(screen.getByText('31')).toBeInTheDocument()
      expect(screen.getByText('24')).toBeInTheDocument()
    })

    it('shows "Final" status for completed games', () => {
      renderWithRouter(<GameBox game={mockGame} />)

      expect(screen.getByText('Final')).toBeInTheDocument()
    })

    it('renders team records', () => {
      renderWithRouter(<GameBox game={mockGame} />)

      expect(screen.getByText('10-2')).toBeInTheDocument()
      expect(screen.getByText('9-3')).toBeInTheDocument()
    })

    it('renders venue and weather info', () => {
      renderWithRouter(<GameBox game={mockGame} />)

      expect(screen.getByText('GEHA Field')).toBeInTheDocument()
      expect(screen.getByText('45°F')).toBeInTheDocument()
    })

    it('navigates to game detail on click', async () => {
      const user = userEvent.setup()
      renderWithRouter(<GameBox game={mockGame} />)

      const gameBox = document.querySelector('.gamebox')
      await user.click(gameBox)

      expect(mockNavigate).toHaveBeenCalledWith('/game/2025_01_SF_KC')
    })
  })

  describe('Upcoming Game', () => {
    it('shows game time instead of "Final"', () => {
      renderWithRouter(<GameBox game={mockUpcomingGame} />)

      expect(screen.getByText('1:00 PM')).toBeInTheDocument()
      expect(screen.queryByText('Final')).not.toBeInTheDocument()
    })

    it('shows dash for scores on upcoming games', () => {
      renderWithRouter(<GameBox game={mockUpcomingGame} />)

      const dashes = screen.getAllByText('-')
      expect(dashes.length).toBeGreaterThanOrEqual(2)
    })
  })

  describe('Winner Highlighting', () => {
    it('highlights the winning team', () => {
      renderWithRouter(<GameBox game={mockGame} />)

      // KC won (31-24), so the home team row should have the winner class
      const teamRows = document.querySelectorAll('.team-row')
      const awayRow = teamRows[0] // SF (away)
      const homeRow = teamRows[1] // KC (home)

      expect(homeRow).toHaveClass('winner')
      expect(awayRow).not.toHaveClass('winner')
    })
  })
})
