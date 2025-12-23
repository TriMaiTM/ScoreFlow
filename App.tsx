import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider as PaperProvider } from 'react-native-paper';
import { Provider as ReduxProvider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { NavigationContainer } from '@react-navigation/native';

import { store } from './src/store';
import { AppNavigator } from './src/navigation/AppNavigator';
import { lightTheme, darkTheme } from './src/theme';
import { useThemeStore } from './src/store/themeStore';
import { NotificationService } from './src/services/NotificationService';
import { useDispatch } from 'react-redux';
import { Platform } from 'react-native';
import { AuthService } from './src/services/MatchService';
import { setCredentials } from './src/store/slices/authSlice';
import { setUserProfile } from './src/store/slices/userSlice';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

export default function App() {
  useEffect(() => {
    // Initialize notification service
    NotificationService.initialize();

    return () => {
      // Cleanup
    };
  }, []);

  return (
    <ReduxProvider store={store}>
      <QueryClientProvider client={queryClient}>
        <SafeAreaProvider>
          <AppContent />
        </SafeAreaProvider>
      </QueryClientProvider>
    </ReduxProvider>
  );
}

function AppContent() {
  const isDarkMode = useThemeStore((state) => state.isDarkMode);
  const theme = isDarkMode ? darkTheme : lightTheme;
  const dispatch = useDispatch();

  useEffect(() => {
    const restoreSession = async () => {
      try {
        let token: string | null = null;
        if (Platform.OS !== 'web') {
          const SecureStore = await import('expo-secure-store');
          token = await SecureStore.getItemAsync('auth_token');
        } else {
          token = localStorage.getItem('auth_token');
        }

        if (token) {
          console.log("Found token, restoring session...");
          // We have a token, try to fetch user profile
          const response = await AuthService.getMe();
          if (response.success) {
            dispatch(setCredentials({
              token: token,
              userId: response.data.id,
              email: response.data.email
            }));
            dispatch(setUserProfile(response.data));
            console.log("Session restored!");
          }
        }
      } catch (e) {
        console.log("Failed to restore session", e);
      }
    };

    restoreSession();
  }, [dispatch]);

  return (
    <PaperProvider theme={theme}>
      <NavigationContainer theme={theme}>
        <AppNavigator />
        <StatusBar style={isDarkMode ? 'light' : 'dark'} />
      </NavigationContainer>
    </PaperProvider>
  );
}
