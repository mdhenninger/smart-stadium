import React from 'react';
import { clsx } from 'clsx';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  message?: string;
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'medium', 
  message,
  className 
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  return (
    <div className={clsx('flex flex-col items-center justify-center', className)}>
      <div 
        className={clsx(
          'animate-spin rounded-full border-2 border-gray-300 border-t-blue-600',
          sizeClasses[size]
        )}
      />
      {message && (
        <p className="mt-2 text-sm text-gray-400 text-center">
          {message}
        </p>
      )}
    </div>
  );
};

export default LoadingSpinner;