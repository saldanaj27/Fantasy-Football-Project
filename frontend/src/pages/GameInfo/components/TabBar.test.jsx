import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TabBar from './TabBar'

describe('TabBar', () => {
  const mockOnTabChange = vi.fn()

  beforeEach(() => {
    mockOnTabChange.mockClear()
  })

  it('renders all three tabs', () => {
    render(<TabBar activeTab="overview" onTabChange={mockOnTabChange} />)

    expect(screen.getByText('Overview')).toBeInTheDocument()
    expect(screen.getByText('Team Stats')).toBeInTheDocument()
    expect(screen.getByText('Player Stats')).toBeInTheDocument()
  })

  it('marks the active tab with active class', () => {
    render(<TabBar activeTab="overview" onTabChange={mockOnTabChange} />)

    const overviewBtn = screen.getByText('Overview')
    const teamStatsBtn = screen.getByText('Team Stats')

    expect(overviewBtn).toHaveClass('active')
    expect(teamStatsBtn).not.toHaveClass('active')
  })

  it('marks team-stats as active when selected', () => {
    render(<TabBar activeTab="team-stats" onTabChange={mockOnTabChange} />)

    const overviewBtn = screen.getByText('Overview')
    const teamStatsBtn = screen.getByText('Team Stats')

    expect(overviewBtn).not.toHaveClass('active')
    expect(teamStatsBtn).toHaveClass('active')
  })

  it('calls onTabChange with correct tab id when clicked', async () => {
    const user = userEvent.setup()
    render(<TabBar activeTab="overview" onTabChange={mockOnTabChange} />)

    await user.click(screen.getByText('Team Stats'))
    expect(mockOnTabChange).toHaveBeenCalledWith('team-stats')

    await user.click(screen.getByText('Player Stats'))
    expect(mockOnTabChange).toHaveBeenCalledWith('player-stats')

    await user.click(screen.getByText('Overview'))
    expect(mockOnTabChange).toHaveBeenCalledWith('overview')
  })

  it('renders as buttons for accessibility', () => {
    render(<TabBar activeTab="overview" onTabChange={mockOnTabChange} />)

    const buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(3)
  })
})
