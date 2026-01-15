export default function GameTitle({game}) {

  return (
    <div>
      <div>
        <div>
          <h1>
            {game.away_team.abbreviation} @ {game.home_team.abbreviation}
          </h1>
          <div>
            <p>Date: {game.date}</p>
            <p>Time: {game.time}</p>
          </div>
        </div>
        
        <div>
          <div>
            {game.away_score} - {game.home_score}
          </div>
          <div>Final Score</div>
        </div>
      </div>
    </div>
  )
}