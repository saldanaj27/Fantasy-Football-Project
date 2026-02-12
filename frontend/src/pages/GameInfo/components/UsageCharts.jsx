import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import "../styles/UsageCharts.css"

// Color palette for charts
const COLORS = ['#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6']
const PASS_RUN_COLORS = ['#3b82f6', '#22c55e']

function ChartTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    return (
      <div className="chart-tooltip">
        <p className="tooltip-name">{data.fullName || data.name}</p>
        <p className="tooltip-value">{data.value.toFixed(1)}%</p>
      </div>
    )
  }
  return null
}

export default function UsageCharts({ usageMetrics }) {
  // Prepare pass/run split data
  const passRunData = [
    { name: 'Pass', value: usageMetrics.pass_run_split.pass_percentage },
    { name: 'Run', value: usageMetrics.pass_run_split.rush_percentage }
  ]

  // Prepare target share data (top 5)
  const targetShareData = usageMetrics.target_share
    .slice(0, 5)
    .map(player => ({
      name: player.name.split(' ').pop(), // Last name only
      value: player.target_share_percentage,
      fullName: player.name,
      position: player.position
    }))

  // Prepare carry share data
  const carryShareData = usageMetrics.carry_share
    .map(player => ({
      name: player.name.split(' ').pop(),
      value: player.carry_share_percentage,
      fullName: player.name,
      position: player.position
    }))

  const renderCustomLabel = ({ name, value }) => `${name} ${value.toFixed(0)}%`

  return (
    <div className="usage-charts-container">
      {/* Pass/Run Split */}
      <div className="chart-card">
        <h5 className="chart-title">Pass/Run Split</h5>
        <ResponsiveContainer width="100%" height={160}>
          <PieChart>
            <Pie
              data={passRunData}
              cx="50%"
              cy="50%"
              innerRadius={35}
              outerRadius={55}
              paddingAngle={2}
              dataKey="value"
              label={renderCustomLabel}
              labelLine={false}
            >
              {passRunData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={PASS_RUN_COLORS[index]} />
              ))}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Target Share */}
      <div className="chart-card">
        <h5 className="chart-title">Target Share (WR/TE)</h5>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={targetShareData}
              cx="50%"
              cy="40%"
              innerRadius={30}
              outerRadius={50}
              paddingAngle={2}
              dataKey="value"
            >
              {targetShareData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
            <Legend
              layout="horizontal"
              align="center"
              verticalAlign="bottom"
              formatter={(value, entry) => (
                <span className="legend-text">{value} ({entry.payload.value.toFixed(0)}%)</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Carry Share */}
      <div className="chart-card">
        <h5 className="chart-title">RB Carry Share</h5>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={carryShareData}
              cx="50%"
              cy="40%"
              innerRadius={30}
              outerRadius={50}
              paddingAngle={2}
              dataKey="value"
            >
              {carryShareData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
            <Legend
              layout="horizontal"
              align="center"
              verticalAlign="bottom"
              formatter={(value, entry) => (
                <span className="legend-text">{value} ({entry.payload.value.toFixed(0)}%)</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
