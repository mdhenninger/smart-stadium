import type { GameSnapshot } from '../types';
import type { MonitoredGame } from '../api/client';
import { formatTimestamp } from '../lib/time';

interface MonitoredGameRowProps {
  game: GameSnapshot;
  monitoredGame: MonitoredGame;
  onRemove: (gameId: string) => void;
}

const statusCopy: Record<string, string> = {
  pre: 'Pre-game',
  in: '🔴 LIVE',
  post: 'Final',
  unknown: 'Unknown',
};

export const MonitoredGameRow = ({ game, monitoredGame, onRemove }: MonitoredGameRowProps) => {
  const status = statusCopy[game.status] ?? game.status;
  const redZone = game.red_zone?.active ? game.red_zone.team_abbr : null;

  const isHomeMonitored = monitoredGame.monitored_teams.includes(game.home.abbreviation);
  const isAwayMonitored = monitoredGame.monitored_teams.includes(game.away.abbreviation);
  const bothMonitored = isHomeMonitored && isAwayMonitored;

  // Determine which team has possession
  const possessionTeam = game.situation?.possession_team_id === game.home.team_id 
    ? game.home.abbreviation 
    : game.situation?.possession_team_id === game.away.team_id 
    ? game.away.abbreviation 
    : null;

  return (
    <div className="monitored-game-row">
      <div className="monitored-game-row__header">
        <span className="monitored-game-row__status">{status}</span>
        <span className="monitored-game-row__timestamp">Updated {formatTimestamp(game.last_update)}</span>
      </div>

      <div className="monitored-game-row__teams">
        <div className={`monitored-game-row__team ${isHomeMonitored ? 'monitored-game-row__team--monitored' : ''}`}>
          {isHomeMonitored && <span className="monitor-icon">🔔</span>}
          {game.home.logo_url && (
            <img 
              src={game.home.logo_url} 
              alt={`${game.home.display_name} logo`}
              className="team-logo"
            />
          )}
          <span className="team-name">{game.home.display_name}</span>
          <span className="team-score">{game.home.score}</span>
        </div>
        <div className={`monitored-game-row__team ${isAwayMonitored ? 'monitored-game-row__team--monitored' : ''}`}>
          {isAwayMonitored && <span className="monitor-icon">🔔</span>}
          {game.away.logo_url && (
            <img 
              src={game.away.logo_url} 
              alt={`${game.away.display_name} logo`}
              className="team-logo"
            />
          )}
          <span className="team-name">{game.away.display_name}</span>
          <span className="team-score">{game.away.score}</span>
        </div>
      </div>

      {/* Game situation for in-progress games */}
      {game.status === 'in' && game.situation && (
        <div className="monitored-game-row__situation">
          {possessionTeam && (
            <span className="situation-possession">
              🏈 {possessionTeam} has possession
            </span>
          )}
          {game.situation.down_distance && (
            <span className="situation-down">
              {game.situation.down_distance}
            </span>
          )}
          {game.situation.field_position && (
            <span className="situation-field">
              at {game.situation.field_position}
            </span>
          )}
          {game.situation.clock && game.situation.period && (
            <span className="situation-clock">
              {game.situation.clock} - Q{game.situation.period}
            </span>
          )}
        </div>
      )}

      {redZone && (
        <div className="monitored-game-row__redzone">
          🏈 Red zone: {redZone}
        </div>
      )}

      <div className="monitored-game-row__footer">
        {bothMonitored && (
          <span className="monitor-badge">Monitoring both teams</span>
        )}
        <button
          type="button"
          className="btn btn--small btn--danger"
          onClick={() => onRemove(game.id)}
        >
          Stop Monitoring
        </button>
      </div>
    </div>
  );
};
