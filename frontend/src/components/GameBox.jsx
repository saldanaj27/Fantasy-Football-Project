import "./GameBox.css"

export default function GameBox({ game }) {
  const gameBoxContainer = "gamebox-container"
  const gameBoxTitle = "gamebox-title"
  const gameBoxText = "gamebox-text"

  if (game.home_score !== null) {
    gameBoxContainer += ' finished-game'
    gameBoxTitle += ' finished-game'
    gameBoxText += ' finished-game'
  }

  return (
    <div className={gameBoxContainer}>
        <h3 className={gameBoxTitle}>
          {game.away_team.abbreviation} @ {game.home_team.abbreviation}
        </h3>

        <p className={gameBoxText}>{game.date}</p>
        <p className={gameBoxText}>{game.time}</p>
    </div>
  )
}