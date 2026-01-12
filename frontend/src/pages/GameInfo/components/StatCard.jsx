export default function StatCard({ title, value, subtitle }) {

  return (
    <div>
      <div>{title}</div>
      <div>{value}</div>
      {subtitle && <div>{subtitle}</div>}
    </div>
  )
}