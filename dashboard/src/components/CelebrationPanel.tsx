import type { FormEvent } from 'react';
import { useMemo, useState } from 'react';
import { Card } from './Card';
import { useTriggerCelebration } from '../hooks/useCelebrationsHistory';
import { Loader } from './feedback/Loader';
import { TeamSelect } from './TeamSelect';
import type { TeamOption } from '../types';

const EVENT_TYPES = [
  { value: 'touchdown', label: 'Touchdown' },
  { value: 'field_goal', label: 'Field Goal' },
  { value: 'extra_point', label: 'Extra Point' },
  { value: 'two_point', label: 'Two-Point' },
  { value: 'safety', label: 'Safety' },
  { value: 'victory', label: 'Victory' },
  { value: 'turnover', label: 'Turnover' },
  { value: 'sack', label: 'Sack' },
  { value: 'big_play', label: 'Big Play' },
];

export const CelebrationPanel = () => {
  const [selectedTeam, setSelectedTeam] = useState<{ sport: string | null; team: TeamOption | null }>({
    sport: null,
    team: null,
  });
  const [eventType, setEventType] = useState(EVENT_TYPES[0].value);
  const [message, setMessage] = useState<string | null>(null);

  const trigger = useTriggerCelebration();

  const isSubmitting = trigger.isPending;

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage(null);

    const team = selectedTeam.team;
    if (!team) {
      setMessage('Please select a team');
      return;
    }
    const sport = selectedTeam.sport ?? team.sport;

    const payload = {
      team_abbr: team.abbreviation,
      team_name: team.name,
      event_type: eventType,
      sport: sport || null,
      points: null,
      game_id: 'manual',
    };

    trigger.mutate(payload, {
      onSuccess: () => {
        setMessage('Celebration launched');
      },
      onError: (error: unknown) => {
        const text = error instanceof Error ? error.message : 'Failed to trigger celebration';
        setMessage(text);
      },
    });
  };

  const feedbackClass = useMemo(() => {
    if (!message) {
      return 'celebration-feedback';
    }
    return trigger.isError ? 'celebration-feedback celebration-feedback--error' : 'celebration-feedback';
  }, [message, trigger.isError]);

  return (
    <Card title="Manual celebrations" subtitle="Trigger lighting effects">
      <form className="celebration-form" onSubmit={handleSubmit}>
        <TeamSelect value={selectedTeam} onChange={setSelectedTeam} />
        <div className="form-grid">
          <label>
            Event type
            <select value={eventType} onChange={(event) => setEventType(event.target.value)}>
              {EVENT_TYPES.map((event) => (
                <option key={event.value} value={event.value}>
                  {event.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '16px' }}>
          <button type="submit" className="btn btn--primary" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader size="small" /> launching…
              </>
            ) : (
              'Launch celebration'
            )}
          </button>
        </div>
        <div className={feedbackClass}>{message ?? 'Use this to test lighting cues without live games.'}</div>
      </form>
    </Card>
  );
};
