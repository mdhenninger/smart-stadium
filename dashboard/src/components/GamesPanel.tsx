import { useState } from 'react';
import { Card } from './Card';
import { Loader } from './feedback/Loader';
import { useGames } from '../hooks/useGames';
import { DEFAULT_SPORT } from '../lib/config';
import { formatTimestamp } from '../lib/time';
import type { GameSnapshot, SportCode } from '../types';

const sportLabels: Record<SportCode, string> = {
  nfl: 'NFL',
  college_football: 'College FB',
};

const statusCopy: Record<string, string> = {
  pre: 'Pre-game',
  in: 'Live',
  post: 'Final',
  unknown: 'Unknown',
};

const renderScore = (game: GameSnapshot) => (
  <div className="game-row__score">
    <div>
      <span className="game-row__team">{game.home.display_name}</span>
      <span className="game-row__points">{game.home.score}</span>
    </div>
    <div>
      <span className="game-row__team">{game.away.display_name}</span>
      <span className="game-row__points">{game.away.score}</span>
    </div>
  </div>
);

const GameRow = ({ game }: { game: GameSnapshot }) => {
  const status = statusCopy[game.status] ?? game.status;
  const redZone = game.red_zone?.active ? game.red_zone.team_abbr : null;
  return (
    <li className="game-row">
      <div className="game-row__header">
        <span className="game-row__status">{status}</span>
        <span className="game-row__timestamp">Updated {formatTimestamp(game.last_update)}</span>
      </div>
      {renderScore(game)}
      {redZone ? <span className="game-row__redzone">Red zone: {redZone}</span> : null}
    </li>
  );
};

export const GamesPanel = () => {
  const [sport, setSport] = useState<SportCode>(DEFAULT_SPORT);
  const { data, isLoading, isError, refetch } = useGames(sport);

  return (
    <Card
      title="Live games"
      subtitle={sportLabels[sport]}
      action={
        <div className="sport-switcher">
          {(Object.keys(sportLabels) as SportCode[]).map((code) => (
            <button
              key={code}
              type="button"
              onClick={() => setSport(code)}
              className={code === sport ? 'btn btn--primary' : 'btn'}
            >
              {sportLabels[code]}
            </button>
          ))}
        </div>
      }
    >
      {isLoading ? (
        <div className="panel-empty">
          <Loader />
          <span>Fetching scoreboard…</span>
        </div>
      ) : null}
      {isError ? (
        <div className="panel-empty panel-empty--error">
          <span>Could not load games.</span>
          <button type="button" onClick={() => refetch()}>
            Retry
          </button>
        </div>
      ) : null}
      {!isLoading && !isError && data && data.games.length === 0 ? (
        <div className="panel-empty">
          <span>No tracked games active.</span>
        </div>
      ) : null}
      {!isLoading && !isError && data ? (
        <ul className="game-list">
          {data.games.map((game) => (
            <GameRow key={game.id} game={game} />
          ))}
        </ul>
      ) : null}
    </Card>
  );
};
