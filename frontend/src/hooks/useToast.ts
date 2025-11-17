import { useMemo } from 'react';
import { useToastStore } from '../components/ui/Toast';

/**
 * Hook for triggering toast notifications without importing the Toast component.
 */
export const useToast = () => {
  const addToast = useToastStore((state) => state.addToast);

  return useMemo(
    () => ({
      success: (message: string) => addToast('success', message),
      error: (message: string) => addToast('error', message),
      info: (message: string) => addToast('info', message),
      warning: (message: string) => addToast('warning', message),
    }),
    [addToast],
  );
};
