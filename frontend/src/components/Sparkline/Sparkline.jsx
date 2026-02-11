import { LineChart, Line, ResponsiveContainer } from 'recharts'
import './Sparkline.css'

export default function Sparkline({ data, width = 60, height = 20, color = '#3b82f6' }) {
  if (!data || data.length === 0) return null

  const chartData = data.map((val, i) => ({ i, v: val }))

  return (
    <div className="sparkline" style={{ width, height }}>
      <ResponsiveContainer>
        <LineChart data={chartData}>
          <Line type="monotone" dataKey="v" stroke={color} strokeWidth={1.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
