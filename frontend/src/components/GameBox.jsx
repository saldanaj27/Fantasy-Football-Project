export default function GameBox({ game }) {
  return (
    <div>
        {/* this structure needs to be nicer */}
        <h3>{game.away_team.abbreviation} @ {game.home_team.abbreviation}</h3>
        <p>{game.date}</p>
        <p>{game.time}</p>
    </div>
  )
}