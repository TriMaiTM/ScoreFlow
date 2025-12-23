import React from 'react';
import { View, ScrollView, StyleSheet, Platform, StatusBar } from 'react-native';
import { Text, Switch, Divider, Avatar, Surface, List, Button } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useDispatch, useSelector } from 'react-redux';
import { LinearGradient } from 'expo-linear-gradient';

import * as ImagePicker from 'expo-image-picker';
import { RootState } from '../store';
import { updateNotificationSettings, setUserProfile } from '../store/slices/userSlice';
import { logout } from '../store/slices/authSlice';
import { useThemeStore } from '../store/themeStore';
import { UserService } from '../services/MatchService';

export default function ProfileScreen() {
  const navigation = useNavigation();
  const dispatch = useDispatch();
  const profile = useSelector((state: RootState) => state.user.profile);
  const notificationSettings = profile?.notificationSettings;

  const handlePickAvatar = async () => {
    try {
      // Request permissions
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        alert('Sorry, we need camera roll permissions to make this work!');
        return;
      }

      // Pick image
      let result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.5,
      });

      if (!result.canceled && result.assets[0].uri) {
        // Prepare form data
        const localUri = result.assets[0].uri;
        const filename = localUri.split('/').pop();
        const match = /\.(\w+)$/.exec(filename || '');
        const type = match ? `image/${match[1]}` : `image`;

        const formData = new FormData();

        if (Platform.OS === 'web') {
          // Web: Fetch blob and append
          const res = await fetch(localUri);
          const blob = await res.blob();
          formData.append('file', blob, filename);
        } else {
          // Native: Append ID object
          // @ts-ignore
          formData.append('file', { uri: localUri, name: filename, type });
        }

        // Upload
        const response = await UserService.uploadAvatar(formData);
        if (response.success && profile) {
          // Update redux
          dispatch(setUserProfile({
            ...profile,
            avatarUrl: response.data.avatarUrl
          }));
        }
      }
    } catch (error) {
      console.error('Avatar upload failed:', error);
      alert('Failed to upload avatar');
    }
  };

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
        <Text style={styles.headerTitle}>Cá nhân</Text>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Profile Header */}
        <Surface style={styles.profileCard} elevation={2}>
          <View style={styles.avatarContainer}>
            {profile?.avatarUrl ? (
              <View>
                <Avatar.Image
                  size={80}
                  source={{ uri: `https://scoreflow-backend-5wu8.onrender.com${profile.avatarUrl}` }} // TODO: Use Config/Environment for Base URL
                  style={styles.avatar}
                />
                <Button
                  mode="contained"
                  compact
                  style={styles.editBadge}
                  labelStyle={{ fontSize: 10, marginHorizontal: 0, marginVertical: 0 }}
                  onPress={handlePickAvatar}
                >
                  Chỉnh sửa
                </Button>
              </View>
            ) : (
              <View>
                <Avatar.Text
                  size={80}
                  label={profile?.name ? profile.name.substring(0, 2).toUpperCase() : 'GU'}
                  style={styles.avatar}
                  color="#fff"
                  labelStyle={{ fontWeight: 'bold' }}
                />
                {profile && (
                  <Button
                    mode="contained"
                    compact
                    style={styles.editBadge}
                    labelStyle={{ fontSize: 10, marginHorizontal: 0, marginVertical: 0 }}
                    onPress={handlePickAvatar}
                  >
                    Edit
                  </Button>
                )}
              </View>
            )}
          </View>
          <Text style={styles.name}>{profile?.name || 'Guest User'}</Text>
          <Text style={styles.email}>{profile?.email || 'guest@scoreflow.app'}</Text>

          <Button
            mode="contained"
            onPress={async () => {
              if (profile) {
                // Logout logic
                try {
                  await import('../services/MatchService').then(m => m.AuthService.logout());

                  // Clear storage
                  if (Platform.OS !== 'web') {
                    await import('expo-secure-store').then(SecureStore =>
                      SecureStore.deleteItemAsync('auth_token')
                    );
                  } else {
                    localStorage.removeItem('auth_token');
                  }

                  // Clear redux
                  import('../store/slices/authSlice').then(a => dispatch(a.logout()));
                  // Navigate to Login
                  navigation.reset({
                    index: 0,
                    routes: [{ name: 'Login' }],
                  });
                } catch (error) {
                  console.error("Logout failed", error);
                }
              } else {
                navigation.navigate('Login' as any);
              }
            }}
            style={{ marginTop: 16, borderRadius: 20 }}
          >
            {profile ? 'Đăng xuất' : 'Đăng nhập / Đăng ký'}
          </Button>
        </Surface>

        {/* Settings - Only for logged in users */}
        {profile && (
          <Surface style={styles.sectionCard} elevation={1}>
            <Text style={styles.sectionTitle}>Cài đặt chung</Text>
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <List.Icon icon="theme-light-dark" color="#94A3B8" />
                <Text style={styles.settingLabel}>Chế độ tối</Text>
              </View>
              <Switch value={isDarkMode} onValueChange={toggleTheme} color="#3B82F6" />
            </View>
            <Divider style={styles.divider} />
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <List.Icon icon="bell" color="#94A3B8" />
                <Text style={styles.settingLabel}>Thông báo</Text>
              </View>
              <Switch
                value={notificationSettings?.enabled}
                onValueChange={() => handleNotificationToggle('enabled')}
                color="#3B82F6"
              />
            </View>
          </Surface>
        )}

        {/* Notification Preferences */}
        {profile && notificationSettings?.enabled && (
          <Surface style={styles.sectionCard} elevation={1}>
            <Text style={styles.sectionTitle}>Cài đặt thông báo</Text>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabelSimple}>Khi trận đấu bắt đầu (trước 30 phút)</Text>
              <Switch
                value={notificationSettings.matchStart}
                onValueChange={() => handleNotificationToggle('matchStart')}
                color="#3B82F6"
              />
            </View>
            <Divider style={styles.divider} />

            <View style={styles.settingRow}>
              <Text style={styles.settingLabelSimple}>Bàn thắng</Text>
              <Switch
                value={notificationSettings.goals}
                onValueChange={() => handleNotificationToggle('goals')}
                color="#3B82F6"
              />
            </View>
            <Divider style={styles.divider} />

            <View style={styles.settingRow}>
              <Text style={styles.settingLabelSimple}>Khi trận đấu kết thúc</Text>
              <Switch
                value={notificationSettings.matchEnd}
                onValueChange={() => handleNotificationToggle('matchEnd')}
                color="#3B82F6"
              />
            </View>
            <Divider style={styles.divider} />

            <View style={styles.settingRow}>
              <Text style={styles.settingLabelSimple}>Chỉ cho đội bóng yêu thích</Text>
              <Switch
                value={notificationSettings.favoriteTeamsOnly}
                onValueChange={() => handleNotificationToggle('favoriteTeamsOnly')}
                color="#3B82F6"
              />
            </View>
          </Surface>
        )}

        {/* Favorites Stats - Only for logged in users */}
        {profile && (
          <Surface style={styles.sectionCard} elevation={1}>
            <Text style={styles.sectionTitle}>Ưa thích</Text>
            <View style={styles.statsContainer}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{profile.favoriteTeams?.length || 0}</Text>
                <Text style={styles.statLabel}>Đội bóng</Text>
              </View>
              <View style={styles.verticalDivider} />
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{profile.favoriteLeagues?.length || 0}</Text>
                <Text style={styles.statLabel}>Giải đấu</Text>
              </View>
              <View style={styles.verticalDivider} />
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{profile.followedMatches?.length || 0}</Text>
                <Text style={styles.statLabel}>Trận đấu</Text>
              </View>
            </View>
          </Surface>
        )}

        {/* Guest Message */}
        {!profile && (
          <Surface style={[styles.sectionCard, { backgroundColor: 'rgba(59, 130, 246, 0.1)', borderColor: '#3B82F6' }]} elevation={0}>
            <Text style={{ color: '#fff', textAlign: 'center', fontSize: 16 }}>
              Đăng nhập để tùy chỉnh thông báo và theo dõi đội bóng bạn yêu thích !
            </Text>
          </Surface>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  // ... existing styles
  editBadge: {
    position: 'absolute',
    bottom: -4,
    right: -10,
    backgroundColor: '#3B82F6',
    borderRadius: 20,
    minWidth: 40,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10
  },
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
