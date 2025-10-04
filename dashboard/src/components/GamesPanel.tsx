import { useState } from 'react';
import { Card } from './Card';
import { Loader } from './feedback/Loader';
import { MonitoringModal } from './MonitoringModal';
import { MonitoredGameRow } from './MonitoredGameRow';
import { useGames } from '../hooks/useGames';
import { useMonitoring } from '../hooks/useMonitoring';
import { DEFAULT_SPORT } from '../lib/config';
import { formatTimestamp } from '../lib/time';
import type { GameSnapshot, SportCode } from '../types';
import type { MonitoringRequest } from '../api/client';

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

interface GameRowProps {
  game: GameSnapshot;
  onSelect: () => void;
}

const GameRow = ({ game, onSelect }: GameRowProps) => {
  const status = statusCopy[game.status] ?? game.status;
  const redZone = game.red_zone?.active ? game.red_zone.team_abbr : null;
  
  // Determine which team has possession
  const possessionTeam = game.situation?.possession_team_id === game.home.team_id 
    ? game.home.abbreviation 
    : game.situation?.possession_team_id === game.away.team_id 
    ? game.away.abbreviation 
    : null;
  
  return (
    <li className="game-row game-row--clickable" onClick={onSelect}>
      <div className="game-row__header">
        <span className="game-row__status">{status}</span>
        <span className="game-row__timestamp">Updated {formatTimestamp(game.last_update)}</span>
      </div>
      {renderScore(game)}
      
      {/* Game situation for in-progress games */}
      {game.status === 'in' && game.situation && (
        <div className="game-row__situation">
          {possessionTeam && (
            <span className="situation-possession">
              🏈 {possessionTeam}
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
      
      {redZone ? <span className="game-row__redzone">Red zone: {redZone}</span> : null}
      <div className="game-row__action">
        <button type="button" className="btn btn--small btn--primary">
          Monitor Game
        </button>
      </div>
    </li>
  );
};

export const GamesPanel = () => {
  const [sport, setSport] = useState<SportCode>(DEFAULT_SPORT);
  const { data, isLoading, isError, refetch } = useGames(sport);
  const { monitoredGames, addGame, removeGame, isGameMonitored } = useMonitoring();
  
  const [showModal, setShowModal] = useState(false);
  const [selectedGame, setSelectedGame] = useState<GameSnapshot | null>(null);

  const handleGameSelect = (game: GameSnapshot) => {
    setSelectedGame(game);
    setShowModal(true);
  };

  const handleMonitoringConfirm = async (request: MonitoringRequest) => {
    try {
      await addGame(request);
      setShowModal(false);
      setSelectedGame(null);
    } catch (error) {
      console.error('Failed to add monitoring:', error);
      // TODO: Show error toast
    }
  };

  const handleRemoveMonitoring = async (gameId: string) => {
    try {
      await removeGame(gameId);
    } catch (error) {
      console.error('Failed to remove monitoring:', error);
      // TODO: Show error toast
    }
  };

  // Get monitored games that match current sport
  const monitoredGamesForSport = monitoredGames.filter((mg) => mg.sport === sport);
  
  // Get game details for monitored games
  const monitoredGameDetails = monitoredGamesForSport
    .map((mg) => {
      const game = data?.games.find((g) => g.id === mg.game_id);
      return game ? { game, monitoredGame: mg } : null;
    })
    .filter((item) => item !== null);

  // Filter out monitored games from available games list
  const availableGames = data?.games.filter((game) => !isGameMonitored(game.id)) ?? [];

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
      {/* Monitored Games Section */}
      {monitoredGameDetails.length > 0 && (
        <section className="monitored-games-section">
          <h3 className="section-title">📺 Monitored Games</h3>
          <div className="monitored-games-list">
            {monitoredGameDetails.map(({ game, monitoredGame }) => (
              <MonitoredGameRow
                key={game.id}
                game={game}
                monitoredGame={monitoredGame}
                onRemove={handleRemoveMonitoring}
              />
            ))}
          </div>
        </section>
      )}

      {/* Available Games Section */}
      <section className="available-games-section">
        <h3 className="section-title">
          📋 {availableGames.length > 0 ? 'Available Games' : 'All Games'}
        </h3>
        
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
        
        {!isLoading && !isError && availableGames.length === 0 && monitoredGameDetails.length === 0 ? (
          <div className="panel-empty">
            <span>No games available.</span>
          </div>
        ) : null}
        
        {!isLoading && !isError && availableGames.length === 0 && monitoredGameDetails.length > 0 ? (
          <div className="panel-empty">
            <span>All games are being monitored.</span>
          </div>
        ) : null}
        
        {!isLoading && !isError && availableGames.length > 0 ? (
          <ul className="game-list">
            {availableGames.map((game) => (
              <GameRow
                key={game.id}
                game={game}
                onSelect={() => handleGameSelect(game)}
              />
            ))}
          </ul>
        ) : null}
      </section>

      {/* Monitoring Modal */}
      {showModal && selectedGame && (
        <MonitoringModal
          game={selectedGame}
          onClose={() => {
            setShowModal(false);
            setSelectedGame(null);
          }}
          onConfirm={handleMonitoringConfirm}
        />
      )}
    </Card>
  );
};
