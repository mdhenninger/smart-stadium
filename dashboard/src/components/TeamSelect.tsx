import { useMemo, useState } from 'react';
import type React from 'react';
import type { TeamOption, TeamSportCode } from '../types';
import { useTeams } from '../hooks/useTeams';

const SPORTS: { code: TeamSportCode; label: string }[] = [
  { code: 'nfl', label: 'NFL' },
  { code: 'cfb', label: 'CFB' },
  { code: 'nhl', label: 'NHL' },
  { code: 'nba', label: 'NBA' },
  { code: 'mlb', label: 'MLB' },
];

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
      <div className="sport-toggle" style={{ display: 'flex', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
        <button
          type="button"
          className={!selectedSport ? 'btn btn--secondary btn--active' : 'btn btn--secondary'}
          onClick={() => handleSportClick(null)}
        >
          All
        </button>
        {SPORTS.map((s) => (
          <button
            key={s.code}
            type="button"
            className={selectedSport === s.code ? 'btn btn--secondary btn--active' : 'btn btn--secondary'}
            onClick={() => handleSportClick(s.code)}
          >
            {s.label}
          </button>
        ))}
      </div>

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

      <div style={{ marginTop: 8 }}>{colorPreview}</div>
    </div>
  );
};
