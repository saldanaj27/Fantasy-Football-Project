import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import '../styles/StatTrendCharts.css'

const COLORS = ['#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6']

export default function StatTrendCharts({ games }) {
  if (!games || games.length === 0) return null

  // Chronological order (games come in reverse chronological from API)
  const chartData = [...games].reverse().map(g => ({
    week: `Wk ${g.week}`,
    points: g.team_score,
    passYards: g.pass_yards,
    rushYards: g.rush_yards,
  }))

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="trend-tooltip">
          <p className="trend-tooltip-label">{label}</p>
          {payload.map((entry, i) => (
            <p key={i} className="trend-tooltip-value" style={{ color: entry.color }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="stat-trend-charts">
      <div className="trend-chart-card">
        <h5 className="trend-chart-title">Points Per Game</h5>
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
            <XAxis dataKey="week" tick={{ fontSize: 11 }} stroke="var(--text-tertiary)" />
            <YAxis tick={{ fontSize: 11 }} stroke="var(--text-tertiary)" />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="points" name="Points" stroke={COLORS[0]} fill={COLORS[0]} fillOpacity={0.2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="trend-chart-card">
        <h5 className="trend-chart-title">Pass vs Rush Yards</h5>
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
            <XAxis dataKey="week" tick={{ fontSize: 11 }} stroke="var(--text-tertiary)" />
            <YAxis tick={{ fontSize: 11 }} stroke="var(--text-tertiary)" />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Area type="monotone" dataKey="passYards" name="Pass Yds" stackId="1" stroke={COLORS[0]} fill={COLORS[0]} fillOpacity={0.3} />
            <Area type="monotone" dataKey="rushYards" name="Rush Yds" stackId="1" stroke={COLORS[2]} fill={COLORS[2]} fillOpacity={0.3} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
