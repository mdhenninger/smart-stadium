import { useMemo, useState } from 'react';
import type React from 'react';
import type { TeamOption, TeamSportCode } from '../types';
import { useTeams } from '../hooks/useTeams';

const SPORTS: { code: TeamSportCode; label: string; logo: string }[] = [
  { code: 'nfl', label: 'NFL', logo: 'https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png' },
  { code: 'cfb', label: 'CFB', logo: 'https://a.espncdn.com/redesign/assets/img/icons/ESPN-icon-football-college.png' },
  { code: 'nhl', label: 'NHL', logo: 'https://a.espncdn.com/i/teamlogos/leagues/500/nhl.png' },
  { code: 'nba', label: 'NBA', logo: 'https://a.espncdn.com/i/teamlogos/leagues/500/nba.png' },
  { code: 'mlb', label: 'MLB', logo: 'https://a.espncdn.com/i/teamlogos/leagues/500/mlb.png' },
];

// SVG data URI for "All" icon - a grid of 4 squares representing all sports
const ALL_SPORTS_ICON = 'data:image/svg+xml,' + encodeURIComponent(`
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
    <rect x="2" y="2" width="9" height="9" rx="1" opacity="0.7"/>
    <rect x="13" y="2" width="9" height="9" rx="1" opacity="0.7"/>
    <rect x="2" y="13" width="9" height="9" rx="1" opacity="0.7"/>
    <rect x="13" y="13" width="9" height="9" rx="1" opacity="0.7"/>
  </svg>
`);

export interface TeamSelectValue {
  sport: string | null;
  team: TeamOption | null;
}

export interface TeamSelectProps {
  value: TeamSelectValue;
  onChange: (next: TeamSelectValue) => void;
}

export const TeamSelect = ({ value, onChange }: TeamSelectProps) => {
  const [selectedSport, setSelectedSport] = useState<string | null>(null);
  const { data: teams = [], isLoading, isError } = useTeams(selectedSport ?? undefined);

  const filteredTeams = useMemo(() => {
    if (!selectedSport) return teams;
    return teams.filter((t) => t.sport === selectedSport);
  }, [teams, selectedSport]);

  const currentTeam = value.team;

  const handleSportClick = (code: string | null) => {
    setSelectedSport(code);
    // Clear team if sport changes and no longer matches
    if (currentTeam && code && currentTeam.sport !== code) {
      onChange({ sport: code, team: null });
    } else {
      onChange({ sport: code, team: currentTeam });
    }
  };

  const renderColorSwatch = (rgb: [number, number, number]) => {
    const [r, g, b] = rgb;
    const style: React.CSSProperties = {
      width: 16,
      height: 16,
      borderRadius: 3,
      backgroundColor: `rgb(${r}, ${g}, ${b})`,
      border: '1px solid rgba(0,0,0,0.2)',
      display: 'inline-block',
      marginRight: 6,
    };
    return <span style={style} />;
  };

  const colorPreview = useMemo(() => {
    if (!currentTeam) return null;
    const c = currentTeam.colors;
    const primary = c.lighting_primary ?? c.primary;
    const secondary = c.lighting_secondary ?? c.secondary;
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {renderColorSwatch(primary)}
        {renderColorSwatch(secondary)}
      </div>
    );
  }, [currentTeam]);

  return (
    <div className="team-select">
      <div className="sport-toggle" style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'nowrap' }}>
        {SPORTS.map((s) => (
          <button
            key={s.code}
            type="button"
            className={selectedSport === s.code ? 'btn btn--secondary btn--active' : 'btn btn--secondary'}
            onClick={() => handleSportClick(s.code)}
            title={s.label}
          >
            <img src={s.logo} alt={s.label} style={{ width: '24px', height: '24px', display: 'block' }} />
          </button>
        ))}
        <button
          type="button"
          className={!selectedSport ? 'btn btn--secondary btn--active' : 'btn btn--secondary'}
          onClick={() => handleSportClick(null)}
          title="All Sports"
        >
          <img src={ALL_SPORTS_ICON} alt="All" style={{ width: '24px', height: '24px', display: 'block' }} />
        </button>
      </div>

      <div className="form-grid">
        <label>
          Team
          <select
            value={currentTeam?.value ?? ''}
            onChange={(e) => {
              const val = e.target.value;
              const t = filteredTeams.find((x) => x.value === val) ?? null;
              onChange({ sport: selectedSport, team: t });
            }}
          >
            <option value="" disabled>
              {isLoading ? 'Loading teams…' : isError ? 'Failed to load teams' : 'Select a team'}
            </option>
            {filteredTeams.map((t) => (
              <option key={t.value} value={t.value}>
                {selectedSport ? t.name : t.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div style={{ marginTop: 8 }}>{colorPreview}</div>
    </div>
  );
};
