import clsx from 'clsx';

interface LoaderProps {
  size?: 'small' | 'medium';
}

export const Loader = ({ size = 'medium' }: LoaderProps) => (
  <span className={clsx('loader', `loader--${size}`)} aria-hidden="true" />
);
