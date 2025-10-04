import type { ReactNode } from 'react';
import clsx from 'clsx';

interface CardProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export const Card = ({ title, subtitle, action, children, className }: CardProps) => {
  return (
    <section className={clsx('card', className)}>
      <header className="card__header">
        <div>
          <h2>{title}</h2>
          {subtitle && <p className="card__subtitle">{subtitle}</p>}
        </div>
        {action ? <div className="card__action">{action}</div> : null}
      </header>
      <div className="card__body">{children}</div>
    </section>
  );
};
