import '../styles/TabBar.css'

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'team-stats', label: 'Team Stats' },
  { id: 'player-stats', label: 'Player Stats' },
]

export default function TabBar({ activeTab, onTabChange }) {
  return (
    <div className="tab-bar">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}
