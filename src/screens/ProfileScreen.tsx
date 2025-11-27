import React from 'react';
import { View, ScrollView, StyleSheet, Platform, StatusBar } from 'react-native';
import { Text, Switch, Divider, Avatar, Surface, List } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useDispatch, useSelector } from 'react-redux';
import { LinearGradient } from 'expo-linear-gradient';

import { RootState } from '../store';
import { updateNotificationSettings } from '../store/slices/userSlice';
import { useThemeStore } from '../store/themeStore';

export default function ProfileScreen() {
  const navigation = useNavigation();
  const dispatch = useDispatch();
  const profile = useSelector((state: RootState) => state.user.profile);
  const notificationSettings = profile?.notificationSettings;

  const isDarkMode = useThemeStore((state) => state.isDarkMode);
  const toggleTheme = useThemeStore((state) => state.toggleTheme);

  const handleNotificationToggle = (setting: keyof typeof notificationSettings) => {
    if (notificationSettings) {
      dispatch(
        updateNotificationSettings({
          ...notificationSettings,
          [setting]: !notificationSettings[setting],
        })
      );
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0F172A" />
      <LinearGradient
        colors={['#0F172A', '#1E293B', '#0F172A']}
        style={StyleSheet.absoluteFill}
      />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Profile</Text>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Profile Header */}
        <Surface style={styles.profileCard} elevation={2}>
          <View style={styles.avatarContainer}>
            <Avatar.Text
              size={80}
              label={profile?.name ? profile.name.substring(0, 2).toUpperCase() : 'GU'}
              style={styles.avatar}
              color="#fff"
              labelStyle={{ fontWeight: 'bold' }}
            />
          </View>
          <Text style={styles.name}>{profile?.name || 'Guest User'}</Text>
          <Text style={styles.email}>{profile?.email || 'guest@scoreflow.app'}</Text>
        </Surface>

        {/* Settings */}
        <Surface style={styles.sectionCard} elevation={1}>
          <Text style={styles.sectionTitle}>⚙️ Settings</Text>
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <List.Icon icon="theme-light-dark" color="#94A3B8" />
              <Text style={styles.settingLabel}>Dark Mode</Text>
            </View>
            <Switch value={isDarkMode} onValueChange={toggleTheme} color="#3B82F6" />
          </View>
          <Divider style={styles.divider} />
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <List.Icon icon="bell" color="#94A3B8" />
              <Text style={styles.settingLabel}>Notifications</Text>
            </View>
            <Switch
              value={notificationSettings?.enabled}
              onValueChange={() => handleNotificationToggle('enabled')}
              color="#3B82F6"
            />
          </View>
        </Surface>

        {/* Notification Preferences */}
        {notificationSettings?.enabled && (
          <Surface style={styles.sectionCard} elevation={1}>
            <Text style={styles.sectionTitle}>🔔 Notification Preferences</Text>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabelSimple}>Match Start (30 min before)</Text>
              <Switch
                value={notificationSettings.matchStart}
                onValueChange={() => handleNotificationToggle('matchStart')}
                color="#3B82F6"
              />
            </View>
            <Divider style={styles.divider} />

            <View style={styles.settingRow}>
              <Text style={styles.settingLabelSimple}>Goals</Text>
              <Switch
                value={notificationSettings.goals}
                onValueChange={() => handleNotificationToggle('goals')}
                color="#3B82F6"
              />
            </View>
            <Divider style={styles.divider} />

            <View style={styles.settingRow}>
              <Text style={styles.settingLabelSimple}>Match End</Text>
              <Switch
                value={notificationSettings.matchEnd}
                onValueChange={() => handleNotificationToggle('matchEnd')}
                color="#3B82F6"
              />
            </View>
            <Divider style={styles.divider} />

            <View style={styles.settingRow}>
              <Text style={styles.settingLabelSimple}>Favorite Teams Only</Text>
              <Switch
                value={notificationSettings.favoriteTeamsOnly}
                onValueChange={() => handleNotificationToggle('favoriteTeamsOnly')}
                color="#3B82F6"
              />
            </View>
          </Surface>
        )}

        {/* Favorites Stats */}
        <Surface style={styles.sectionCard} elevation={1}>
          <Text style={styles.sectionTitle}>⭐ Favorites</Text>
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{profile?.favoriteTeams.length || 0}</Text>
              <Text style={styles.statLabel}>Teams</Text>
            </View>
            <View style={styles.verticalDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{profile?.favoriteLeagues.length || 0}</Text>
              <Text style={styles.statLabel}>Leagues</Text>
            </View>
            <View style={styles.verticalDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{profile?.followedMatches.length || 0}</Text>
              <Text style={styles.statLabel}>Matches</Text>
            </View>
          </View>
        </Surface>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
  header: {
    paddingTop: Platform.OS === 'android' ? 40 : 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  headerTitle: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  profileCard: {
    backgroundColor: 'rgba(30, 41, 59, 0.6)',
    borderRadius: 24,
    padding: 24,
    alignItems: 'center',
    marginBottom: 24,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  avatarContainer: {
    marginBottom: 16,
    shadowColor: '#3B82F6',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  avatar: {
    backgroundColor: '#3B82F6',
  },
  name: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  email: {
    color: '#94A3B8',
    fontSize: 14,
  },
  sectionCard: {
    backgroundColor: 'rgba(30, 41, 59, 0.6)',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  settingInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingLabel: {
    color: '#CBD5E1',
    fontSize: 16,
    marginLeft: 8,
  },
  settingLabelSimple: {
    color: '#CBD5E1',
    fontSize: 16,
  },
  divider: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    marginVertical: 8,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingVertical: 8,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    color: '#3B82F6',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statLabel: {
    color: '#94A3B8',
    fontSize: 12,
  },
  verticalDivider: {
    width: 1,
    height: 40,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
});
