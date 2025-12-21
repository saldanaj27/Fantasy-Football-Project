import "./GameBox.css"

export default function GameBox({ game }) {
  return (
    <div className="gamebox-container">
        <h3 className="gamebox-title">
          {game.away_team.abbreviation} @ {game.home_team.abbreviation}
        </h3>

        <p className="gamebox-text">{game.date}</p>
        <p className="gamebox-text">{game.time}</p>
    </div>
  )
}