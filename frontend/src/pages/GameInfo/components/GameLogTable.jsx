import TeamLogo from '../../../components/TeamLogo/TeamLogo'
import '../styles/GameLogTable.css'

export default function GameLogTable({ games }) {
  if (!games || games.length === 0) {
    return <div className="no-data">No game log data available</div>
  }

  return (
    <div className="game-log-container">
      <h5 className="game-log-title">Game Log</h5>
      <div className="game-log-scroll">
        <table className="game-log-table">
          <thead>
            <tr>
              <th>Wk</th>
              <th>Opp</th>
              <th>Result</th>
              <th>Score</th>
              <th>Pass Yds</th>
              <th>Rush Yds</th>
              <th>Total Yds</th>
              <th>TOs</th>
            </tr>
          </thead>
          <tbody>
            {games.map((game) => (
              <tr key={game.game_id} className={`result-${game.result.toLowerCase()}`}>
                <td>{game.week}</td>
                <td className="opp-cell">
                  <span className="home-away">{game.is_home ? 'vs' : '@'}</span>
                  <TeamLogo logoUrl={game.opponent_logo_url} abbreviation={game.opponent} size="sm" />
                  {game.opponent}
                </td>
                <td>
                  <span className={`result-badge ${game.result.toLowerCase()}`}>{game.result}</span>
                </td>
                <td>{game.team_score}-{game.opp_score}</td>
                <td>{game.pass_yards}</td>
                <td>{game.rush_yards}</td>
                <td>{game.total_yards}</td>
                <td>{game.turnovers}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
