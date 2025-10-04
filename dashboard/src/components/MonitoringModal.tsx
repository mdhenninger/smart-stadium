import { useState } from 'react';
import type { GameSnapshot, SportCode } from '../types';
import type { MonitoringRequest } from '../api/client';

interface MonitoringModalProps {
  game: GameSnapshot;
  onClose: () => void;
  onConfirm: (request: MonitoringRequest) => void;
}

type TeamSelection = 'home' | 'away' | 'both' | null;

export const MonitoringModal = ({ game, onClose, onConfirm }: MonitoringModalProps) => {
  const [selected, setSelected] = useState<TeamSelection>(null);

  const handleConfirm = () => {
    if (!selected) return;

    let monitored_teams: string[];
    if (selected === 'both') {
      monitored_teams = [game.home.abbreviation, game.away.abbreviation];
    } else if (selected === 'home') {
      monitored_teams = [game.home.abbreviation];
    } else {
      monitored_teams = [game.away.abbreviation];
    }

    const request: MonitoringRequest = {
      game_id: game.id,
      sport: game.sport as SportCode,
      home_team_abbr: game.home.abbreviation,
      away_team_abbr: game.away.abbreviation,
      monitored_teams,
    };

    onConfirm(request);
  };

  const statusLabel = {
    pre: 'Pre-game',
    in: 'Live',
    post: 'Final',
    unknown: 'Unknown',
  }[game.status] ?? game.status;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Monitor Game</h2>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="modal-body">
          <div className="game-info">
            <div className="game-status-badge">{statusLabel}</div>
            <div className="game-matchup">
              {game.away.display_name} @ {game.home.display_name}
            </div>
          </div>

          <p className="team-selection-prompt">Which team(s) do you want to monitor?</p>

          <div className="team-selection-grid">
            <button
              type="button"
              className={`team-card ${selected === 'home' ? 'team-card--selected' : ''}`}
              onClick={() => setSelected('home')}
            >
              <div className="team-card__label">Home Team</div>
              <div className="team-card__name">{game.home.display_name}</div>
              <div className="team-card__abbr">{game.home.abbreviation}</div>
            </button>

            <button
              type="button"
              className={`team-card ${selected === 'away' ? 'team-card--selected' : ''}`}
              onClick={() => setSelected('away')}
            >
              <div className="team-card__label">Away Team</div>
              <div className="team-card__name">{game.away.display_name}</div>
              <div className="team-card__abbr">{game.away.abbreviation}</div>
            </button>

            <button
              type="button"
              className={`team-card team-card--both ${selected === 'both' ? 'team-card--selected' : ''}`}
              onClick={() => setSelected('both')}
            >
              <div className="team-card__label">Both Teams</div>
              <div className="team-card__name">Monitor All</div>
              <div className="team-card__abbr">🔔</div>
            </button>
          </div>

          <div className="celebration-info">
            <p className="celebration-info__title">✅ Celebration events:</p>
            <ul className="celebration-info__list">
              <li>Touchdowns, Field Goals, Extra Points</li>
              <li>Safeties, Two-Point Conversions</li>
              <li>Final Score (when game ends)</li>
            </ul>
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn btn--secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            type="button"
            className="btn btn--primary"
            onClick={handleConfirm}
            disabled={!selected}
          >
            Start Monitoring
          </button>
        </div>
      </div>
    </div>
  );
};
