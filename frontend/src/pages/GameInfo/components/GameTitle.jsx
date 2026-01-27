import "../styles/GameTitle.css"

export default function GameTitle({game}) {

  return (
    <div className="game-title-container">
      <div className="game-title-content">
        <div className="game-title-info">
          <h1>
            {game.away_team.abbreviation} @ {game.home_team.abbreviation}
          </h1>
          <div className="game-title-details">
            <p>Date: {game.date}</p>
            <p>Time: {game.time}</p>
          </div>
        </div>
        
        <div className="game-title-score">
          <div className="game-title-score-value">
            {game.away_score} - {game.home_score}
          </div>
          <div className="game-title-score-label">Final Score</div>
        </div>
      </div>
    </div>
  )
}