import "./GameBox.css"
import { useNavigate } from 'react-router-dom'

export default function GameBox({ game }) {
  const navigate = useNavigate()
  const isFinished = game.home_score !== null

  const handleClick = () => {
    navigate(`/game/${game.id}`)
  }

  return (
    <div
      className={`gamebox-container ${isFinished ? "finished-game" : ""}`}
      onClick={handleClick}
    >
        <h3 className="gamebox-title">
          {game.away_team.abbreviation} @ {game.home_team.abbreviation}
        </h3>

        {/* Show score ONLY if finished */}
        {isFinished && (
          <p className="score">
            {game.away_score} – {game.home_score}
          </p>
        )}

        <p className="gamebox-text">{game.date}</p>
        
        {!isFinished && (
          <p className="gamebox-text">{game.time}</p>
        )}
    </div>
  )
}