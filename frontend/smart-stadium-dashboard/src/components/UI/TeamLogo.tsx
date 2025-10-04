import React from 'react';
import { clsx } from 'clsx';
import { Team } from '../../types';
import { getTeamColors } from '../../utils';

interface TeamLogoProps {
  team: Team;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showName?: boolean;
  className?: string;
}

const TeamLogo: React.FC<TeamLogoProps> = ({
  team,
  size = 'md',
  showName = false,
  className,
}) => {
  const colors = getTeamColors(team);
  
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24',
  };
  
  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
    xl: 'text-lg',
  };
  
  return (
    <div className={clsx('flex items-center space-x-2', className)}>
      {/* Team Color Circle */}
      <div 
        className={clsx(
          'rounded-full border-2 border-white shadow-lg flex items-center justify-center',
          sizeClasses[size]
        )}
        style={{ backgroundColor: colors.primary }}
      >
        {team.logo_url ? (
          <img 
            src={team.logo_url} 
            alt={`${team.name} logo`}
            className="w-full h-full rounded-full object-cover"
          />
        ) : (
          <span 
            className={clsx(
              'font-bold text-white',
              textSizeClasses[size]
            )}
          >
            {team.abbreviation || team.name.substring(0, 2).toUpperCase()}
          </span>
        )}
      </div>
      
      {/* Team Name */}
      {showName && (
        <div className="flex flex-col">
          <span className={clsx('font-medium text-white', textSizeClasses[size])}>
            {team.city}
          </span>
          <span className={clsx('font-bold text-white', textSizeClasses[size])}>
            {team.name}
          </span>
        </div>
      )}
    </div>
  );
};

export default TeamLogo;