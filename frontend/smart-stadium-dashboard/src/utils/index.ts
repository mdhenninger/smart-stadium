import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Utility for combining Tailwind classes with conflict resolution
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format time remaining in a game
export function formatTimeRemaining(timeString: string): string {
  if (!timeString) return '--:--';
  
  // Handle different time formats from ESPN API
  if (timeString.includes(':')) {
    return timeString;
  }
  
  // Convert seconds to MM:SS format
  const totalSeconds = parseInt(timeString);
  if (isNaN(totalSeconds)) return timeString;
  
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// Format game status for display
export function formatGameStatus(status: string): string {
  const statusMap: Record<string, string> = {
    'scheduled': 'Scheduled',
    'in_progress': 'Live',
    'completed': 'Final',
    'postponed': 'Postponed',
    'cancelled': 'Cancelled',
  };
  
  return statusMap[status] || status.replace('_', ' ').toUpperCase();
}

// Get status color for UI elements
export function getStatusColor(status: string): string {
  const colorMap: Record<string, string> = {
    'scheduled': 'bg-blue-600',
    'in_progress': 'bg-green-600',
    'completed': 'bg-gray-600',
    'postponed': 'bg-yellow-600',
    'cancelled': 'bg-red-600',
  };
  
  return colorMap[status] || 'bg-gray-600';
}

// Format date and time for display
export function formatDateTime(dateString: string): {
  date: string;
  time: string;
  relative: string;
} {
  const date = new Date(dateString);
  const now = new Date();
  
  const dateStr = date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
  
  const timeStr = date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });
  
  // Calculate relative time
  const diffMs = date.getTime() - now.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);
  
  let relative: string;
  if (Math.abs(diffMs) < 1000 * 60 * 60) {
    // Less than an hour
    const diffMins = Math.floor(Math.abs(diffMs) / (1000 * 60));
    relative = diffMs < 0 ? `${diffMins}m ago` : `in ${diffMins}m`;
  } else if (Math.abs(diffHours) < 24) {
    // Less than a day
    relative = diffMs < 0 ? `${Math.abs(diffHours)}h ago` : `in ${diffHours}h`;
  } else {
    // Days
    relative = diffMs < 0 ? `${Math.abs(diffDays)}d ago` : `in ${diffDays}d`;
  }
  
  return { date: dateStr, time: timeStr, relative };
}

// Validate team colors and provide fallbacks
export function getTeamColors(team: { colors: { primary: string; secondary: string } }) {
  const validateColor = (color: string): string => {
    // Basic hex color validation
    if (/^#[0-9A-Fa-f]{6}$/.test(color)) {
      return color;
    }
    
    // Fallback colors
    return '#6B7280'; // gray-500
  };
  
  return {
    primary: validateColor(team.colors.primary),
    secondary: validateColor(team.colors.secondary),
  };
}

// Calculate celebration intensity based on play type and score differential
export function calculateCelebrationIntensity(
  playType: string,
  scoreDifferential: number,
  timeRemaining: number
): 'low' | 'medium' | 'high' {
  let baseIntensity: number;
  
  // Base intensity by play type
  switch (playType.toLowerCase()) {
    case 'touchdown':
      baseIntensity = 0.8;
      break;
    case 'field_goal':
      baseIntensity = 0.5;
      break;
    case 'safety':
      baseIntensity = 0.7;
      break;
    case 'interception':
    case 'fumble_recovery':
      baseIntensity = 0.6;
      break;
    case 'sack':
      baseIntensity = 0.4;
      break;
    case 'big_play':
      baseIntensity = 0.5;
      break;
    case 'game_winner':
      baseIntensity = 1.0;
      break;
    default:
      baseIntensity = 0.3;
  }
  
  // Adjust for game situation
  if (timeRemaining < 300) { // Last 5 minutes
    baseIntensity += 0.2;
  }
  
  if (Math.abs(scoreDifferential) <= 7) { // Close game
    baseIntensity += 0.1;
  }
  
  // Convert to intensity levels
  if (baseIntensity >= 0.7) return 'high';
  if (baseIntensity >= 0.4) return 'medium';
  return 'low';
}

// Debounce function for API calls
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
}

// Local storage helpers with error handling
export const storage = {
  get: <T>(key: string, defaultValue: T): T => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.warn(`Failed to parse localStorage item ${key}:`, error);
      return defaultValue;
    }
  },
  
  set: <T>(key: string, value: T): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.warn(`Failed to set localStorage item ${key}:`, error);
    }
  },
  
  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.warn(`Failed to remove localStorage item ${key}:`, error);
    }
  },
};

// Retry helper for async operations
export async function withRetry<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt === maxRetries) {
        throw lastError;
      }
      
      console.warn(`Attempt ${attempt} failed, retrying in ${delay}ms:`, error);
      await new Promise(resolve => setTimeout(resolve, delay * attempt));
    }
  }
  
  throw lastError!;
}