const debugEnabled =
  !import.meta.env.PROD || (import.meta.env.VITE_ENABLE_DEBUG_LOGS ?? '').toLowerCase() === 'true';

export const logDebug = (...args: unknown[]): void => {
  if (debugEnabled) {
    console.debug('[DEBUG]', ...args);
  }
};

export const logInfo = (message: string): void => {
  if (debugEnabled) {
    console.info('[INFO]', message);
  }
};

export const logWarn = (message: string): void => {
  if (debugEnabled) {
    console.warn('[WARN]', message);
  }
};

export const logError = (message: string, err?: unknown): void => {
  if (debugEnabled && err) {
    console.error('[ERROR]', message, err);
  } else {
    console.error('[ERROR]', message);
  }
};
