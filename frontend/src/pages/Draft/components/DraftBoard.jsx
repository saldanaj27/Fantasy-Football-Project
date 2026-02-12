export default function DraftBoard({ board, numTeams, numRounds, userTeamPosition }) {
  if (!board || board.length === 0) {
    return null
  }

  // Build a lookup: picks[round][team] = pick
  const pickMap = {}
  for (const pick of board) {
    if (!pickMap[pick.round_number]) pickMap[pick.round_number] = {}
    pickMap[pick.round_number][pick.team_number] = pick
  }

  return (
    <div className="draft-board">
      <h3 className="board-title">Draft Board</h3>
      <div className="board-scroll">
        <table className="board-table">
          <thead>
            <tr>
              <th className="round-header">Rd</th>
              {Array.from({ length: numTeams }, (_, i) => i + 1).map(t => (
                <th key={t} className={`team-header ${t === userTeamPosition ? 'user-team' : ''}`}>
                  {t === userTeamPosition ? 'You' : `T${t}`}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: numRounds }, (_, i) => i + 1).map(round => (
              <tr key={round}>
                <td className="round-cell">{round}</td>
                {Array.from({ length: numTeams }, (_, i) => i + 1).map(team => {
                  const pick = pickMap[round]?.[team]
                  return (
                    <td
                      key={team}
                      className={`pick-cell ${pick?.is_user ? 'user-pick' : ''} ${team === userTeamPosition ? 'user-column' : ''}`}
                    >
                      {pick ? (
                        <div className="pick-content">
                          <span className={`pick-position pos-${pick.player.position.toLowerCase()}`}>
                            {pick.player.position}
                          </span>
                          <span className="pick-name">{pick.player.name.split(' ').pop()}</span>
                        </div>
                      ) : null}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
