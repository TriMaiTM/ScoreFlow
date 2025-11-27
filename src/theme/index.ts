import { MD3LightTheme, MD3DarkTheme } from 'react-native-paper';
import { DefaultTheme as NavigationLightTheme, DarkTheme as NavigationDarkTheme } from '@react-navigation/native';

const customColors = {
  // Navy Blue Palette
  primary: '#0F172A',      // Deep Navy - Main brand color
  secondary: '#334155',    // Slate - Secondary elements
  tertiary: '#3B82F6',     // Bright Blue - Interactive elements/Accents
  
  // Functional
  background: '#F1F5F9',   // Light Slate Gray - App background
  surface: '#FFFFFF',      // White - Cards/Modals
  error: '#EF4444',        // Red - Errors/Live
  success: '#10B981',      // Emerald - Wins/Success
  warning: '#F59E0B',      // Amber - Warnings
  info: '#3B82F6',         // Blue - Info
  
  // Dark mode specific
  darkBackground: '#020617', // Very dark navy/black
  darkSurface: '#0F172A',    // Deep Navy
  darkCard: '#1E293B',       // Slate 800
};

export const lightTheme = {
  ...MD3LightTheme,
  ...NavigationLightTheme,
  colors: {
    ...MD3LightTheme.colors,
    ...NavigationLightTheme.colors,
    primary: customColors.primary,
    onPrimary: '#FFFFFF',
    primaryContainer: '#E2E8F0',
    onPrimaryContainer: customColors.primary,
    
    secondary: customColors.secondary,
    onSecondary: '#FFFFFF',
    secondaryContainer: '#F1F5F9',
    onSecondaryContainer: customColors.secondary,
    
    tertiary: customColors.tertiary,
    
    background: customColors.background,
    surface: customColors.surface,
    surfaceVariant: '#E2E8F0',
    
    error: customColors.error,
    
    // Custom text colors for better contrast
    text: '#0F172A',
    onSurface: '#1E293B',
    onSurfaceVariant: '#64748B', // Subtext
    
    outline: '#CBD5E1',
    backdrop: 'rgba(15, 23, 42, 0.5)',
    notification: customColors.error,
  },
  roundness: 16, // More modern rounded corners
  dark: false,
};

export const darkTheme = {
  ...MD3DarkTheme,
  ...NavigationDarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    ...NavigationDarkTheme.colors,
    primary: '#60A5FA', // Lighter blue for dark mode
    onPrimary: '#0F172A',
    primaryContainer: '#1E3A8A',
    onPrimaryContainer: '#DBEAFE',
    
    secondary: '#94A3B8',
    onSecondary: '#0F172A',
    secondaryContainer: '#334155',
    onSecondaryContainer: '#E2E8F0',
    
    background: customColors.darkBackground,
    surface: customColors.darkSurface,
    surfaceVariant: customColors.darkCard,
    
    error: '#F87171',
    
    text: '#F8FAFC',
    onSurface: '#F1F5F9',
    onSurfaceVariant: '#94A3B8',
    
    outline: '#334155',
    backdrop: 'rgba(0, 0, 0, 0.7)',
    notification: customColors.error,
  },
  roundness: 16,
  dark: true,
};

export type AppTheme = typeof lightTheme;
