/**
 * Loading Component
 * Reusable loading spinner
 */

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export const Loading = ({ size = 'md', text }: LoadingProps) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className={`${sizeClasses[size]} border-violet-600 border-t-transparent rounded-full animate-spin`}
      />
      {text && <p className="text-gray-400 text-sm">{text}</p>}
    </div>
  );
};

export const LoadingScreen = ({ text = 'Loading...' }: { text?: string }) => {
  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <Loading size="lg" text={text} />
    </div>
  );
};
