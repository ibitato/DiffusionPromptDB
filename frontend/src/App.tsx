/**
 * App Component
 * Main application component with router and auth initialization
 */

import { useEffect } from 'react';
import { AppRouter } from './router/AppRouter';
import { useAuthStore } from './store/authStore';
import { ToastContainer } from './components/ui/Toast';
import { QueryProvider } from './providers/QueryProvider';

function App() {
  const initAuth = useAuthStore((state) => state.initAuth);

  useEffect(() => {
    // Initialize authentication on app load
    initAuth();
  }, [initAuth]);

  return (
    <QueryProvider>
      <AppRouter />
      <ToastContainer />
    </QueryProvider>
  );
}

export default App;
