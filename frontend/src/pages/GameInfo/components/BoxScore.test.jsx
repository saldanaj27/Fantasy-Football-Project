import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import BoxScore from './BoxScore'
import { mockBoxScore } from '../../../test/testUtils'

// Mock the API call
vi.mock('../../../api/analytics', () => ({
  getGameBoxScore: vi.fn(),
}))

import { getGameBoxScore } from '../../../api/analytics'

describe('BoxScore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading state initially', () => {
    getGameBoxScore.mockImplementation(() => new Promise(() => {})) // Never resolves
    render(<BoxScore gameId="2025_01_SF_KC" />)

    expect(screen.getByText('Loading box score...')).toBeInTheDocument()
  })

  it('renders box score data when loaded', async () => {
    getGameBoxScore.mockResolvedValue(mockBoxScore)
    render(<BoxScore gameId="2025_01_SF_KC" />)

    await waitFor(() => {
      expect(screen.getByText('Box Score')).toBeInTheDocument()
    })

    // Check team abbreviations appear (multiple times - header + performers)
    expect(screen.getAllByText('KC').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('SF').length).toBeGreaterThanOrEqual(1)

    // Check stat labels
    expect(screen.getByText('Total Yards')).toBeInTheDocument()
    expect(screen.getByText('Pass Yards')).toBeInTheDocument()
    expect(screen.getByText('Rush Yards')).toBeInTheDocument()
  })

  it('renders top performers section', async () => {
    getGameBoxScore.mockResolvedValue(mockBoxScore)
    render(<BoxScore gameId="2025_01_SF_KC" />)

    await waitFor(() => {
      expect(screen.getByText('Top Performers')).toBeInTheDocument()
    })

    // Check that a performer is shown
    expect(screen.getByText('Patrick Mahomes')).toBeInTheDocument()
    expect(screen.getByText('26.8 pts')).toBeInTheDocument()
  })

  it('renders nothing when error occurs', async () => {
    getGameBoxScore.mockRejectedValue(new Error('Failed to fetch'))
    const { container } = render(<BoxScore gameId="invalid" />)

    await waitFor(() => {
      expect(screen.queryByText('Loading box score...')).not.toBeInTheDocument()
    })

    // Should render nothing on error
    expect(container.querySelector('.box-score')).not.toBeInTheDocument()
  })

  it('displays team stats comparison', async () => {
    getGameBoxScore.mockResolvedValue(mockBoxScore)
    render(<BoxScore gameId="2025_01_SF_KC" />)

    await waitFor(() => {
      expect(screen.getByText('440')).toBeInTheDocument() // KC total yards
      expect(screen.getByText('363')).toBeInTheDocument() // SF total yards
    })
  })
})
