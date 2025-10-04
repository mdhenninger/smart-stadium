import React from 'react';
import { clsx } from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  clickable?: boolean;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  children,
  className,
  padding = 'md',
  hover = false,
  clickable = false,
  onClick,
}) => {
  const baseClasses = 'bg-gray-800 rounded-lg shadow-lg border border-gray-700';
  
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-6',
    lg: 'p-8',
  };
  
  const interactiveClasses = {
    hover: 'hover:bg-gray-700 transition-colors duration-200',
    clickable: 'cursor-pointer hover:shadow-xl hover:border-gray-600 transform hover:-translate-y-1 transition-all duration-200',
  };
  
  return (
    <div
      className={clsx(
        baseClasses,
        paddingClasses[padding],
        {
          [interactiveClasses.hover]: hover,
          [interactiveClasses.clickable]: clickable,
        },
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export default Card;