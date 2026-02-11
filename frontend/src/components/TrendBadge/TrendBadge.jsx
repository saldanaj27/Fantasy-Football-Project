import './TrendBadge.css'

export default function TrendBadge({ trend }) {
  if (!trend) return null

  const config = {
    up: { label: 'UP', className: 'trend-up' },
    down: { label: 'DOWN', className: 'trend-down' },
    stable: { label: 'STABLE', className: 'trend-stable' },
  }

  const { label, className } = config[trend] || config.stable

  return (
    <span className={`trend-badge ${className}`}>
      {trend === 'up' && '▲ '}
      {trend === 'down' && '▼ '}
      {trend === 'stable' && '— '}
      {label}
    </span>
  )
}
