export const queryKeys = {
  status: ['status'] as const,
  devices: ['devices'] as const,
  games: (sport: string) => ['games', sport] as const,
  celebrations: ['celebrations'] as const,
  teams: ['teams'] as const,
};
