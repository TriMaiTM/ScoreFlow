import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  FlatList,
  StatusBar,
  Platform,
  Dimensions,
  ImageBackground,
  Image,
} from 'react-native';
import {
  Text,
  ActivityIndicator,
  Searchbar,
  useTheme,
  Surface,
  IconButton,
  Avatar,
  Badge,
  Button,
} from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { format, addDays, subDays, isToday, formatDistanceToNow } from 'date-fns';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { NotificationGenerator, AppNotification } from '../services/NotificationGenerator';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { MatchService } from '../services/MatchService';
import { Match } from '../types';
import { RootStackParamList } from '../navigation/AppNavigator';

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

const { width } = Dimensions.get('window');

interface DateItem {
  date: Date;
  formattedDate: string;
  dayName: string;
  dayNumber: string;
}

export default function HomeScreen() {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const dateListRef = useRef<FlatList>(null);

  // Generate date range
  const generateDateRange = (): DateItem[] => {
    const dates: DateItem[] = [];
    const today = new Date();
    const startDate = subDays(today, 14);

    for (let i = 0; i < 29; i++) {
      const date = addDays(startDate, i);
      dates.push({
        date,
        formattedDate: format(date, 'yyyy-MM-dd'),
        dayName: format(date, 'EEE'),
        dayNumber: format(date, 'd'),
      });
    }
    return dates;
  };

  const dateRange = generateDateRange();

  const {
    data: matchesData,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['matches-by-date', format(selectedDate, 'yyyy-MM-dd')],
    queryFn: async () => {
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      return await MatchService.getMatchesByDate(dateStr);
    },
    staleTime: 30000,
    refetchInterval: 30000,
  });

  // Auto-scroll to selected date
  useEffect(() => {
    const index = dateRange.findIndex(
      (item) => format(item.date, 'yyyy-MM-dd') === format(selectedDate, 'yyyy-MM-dd')
    );
    if (index !== -1 && dateListRef.current) {
      dateListRef.current.scrollToIndex({ index, animated: true, viewPosition: 0.5 });
    }
  }, [selectedDate]);

  const matchGroups = matchesData?.data?.leagues || [];

  const filteredMatchGroups = matchGroups
    .map((group: any) => ({
      ...group,
      matches: group.matches.filter(
        (match: Match) =>
          match.homeTeam.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          match.awayTeam.name.toLowerCase().includes(searchQuery.toLowerCase())
      ),
    }))
    .filter((group: any) => group.matches.length > 0);

  // Find a featured match (Live or first upcoming)
  const featuredMatch = filteredMatchGroups.flatMap((g: any) => g.matches).find((m: Match) => m.status === 'live')
    || filteredMatchGroups.flatMap((g: any) => g.matches)[0];

  const renderDateItem = ({ item }: { item: DateItem }) => {
    const isSelected = format(item.date, 'yyyy-MM-dd') === format(selectedDate, 'yyyy-MM-dd');

    return (
      <TouchableOpacity
        style={[
          styles.dateItem,
          isSelected && styles.dateItemSelected,
        ]}
        onPress={() => setSelectedDate(item.date)}
      >
        <Text style={[styles.dayName, isSelected ? styles.textSelected : styles.textUnselected]}>
          {item.dayName}
        </Text>
        <Text style={[styles.dayNumber, isSelected ? styles.textSelected : styles.textUnselected]}>
          {item.dayNumber}
        </Text>
        {isToday(item.date) && !isSelected && (
          <View style={styles.todayDot} />
        )}
      </TouchableOpacity>
    );
  };

  // Notification Logic
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const profile = useSelector((state: RootState) => state.user.profile);

  useEffect(() => {
    if (matchesData?.data?.leagues && profile) {
      const allMatches = matchesData.data.leagues.flatMap((l: any) => l.matches); // Logic simplification: using current loaded matches
      const generated = NotificationGenerator.generateNotifications(allMatches, profile);
      setNotifications(generated);
    }
  }, [matchesData, profile]);

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0F172A" />

      {/* Background Gradient */}
      <LinearGradient
        colors={['#0F172A', '#1E293B', '#0F172A']}
        style={StyleSheet.absoluteFill}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      />

      {/* Header */}
      <View style={styles.header}>
        <Image
          source={require('../../assets/logo-scoreflow.png')}
          style={styles.logo}
          resizeMode="contain"
        />
        <TouchableOpacity
          style={styles.iconButton}
          onPress={() => setShowNotifications(!showNotifications)}
        >
          <IconButton icon="bell-outline" iconColor="#fff" size={24} />
          {notifications.length > 0 && <Badge size={8} style={styles.badge} visible={true} />}
        </TouchableOpacity>
      </View>

      {/* Notification Popup */}
      <NotificationPopup
        visible={showNotifications}
        onClose={() => setShowNotifications(false)}
        notifications={notifications}
      />

      {/* Date Strip */}
      <View style={styles.dateStripWrapper}>
        <FlatList
          ref={dateListRef}
          data={dateRange}
          renderItem={renderDateItem}
          keyExtractor={(item) => item.formattedDate}
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.dateStripContent}
          getItemLayout={(data, index) => ({ length: 60, offset: 60 * index, index })}
        />
      </View>

      {/* Main Content */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor="#fff" />
        }
      >
        {/* Featured Match */}
        {featuredMatch && !searchQuery && (
          <View style={styles.featuredSection}>
            <Text style={styles.sectionTitle}>Trận đấu nổi bật</Text>
            <FeaturedMatchCard
              match={featuredMatch}
              onPress={() => navigation.navigate('MatchDetail', { matchId: featuredMatch.id })}
            />
          </View>
        )}

        {/* Search */}
        <Searchbar
          placeholder="Tìm tên đội bóng..."
          onChangeText={setSearchQuery}
          value={searchQuery}
          style={styles.searchbar}
          inputStyle={styles.searchInput}
          iconColor="rgba(255,255,255,0.5)"
          placeholderTextColor="rgba(255,255,255,0.5)"
        />

        {/* Matches List */}
        {isError ? (
          <View style={styles.emptyState}>
            <Text style={[styles.emptyText, { color: '#EF4444' }]}>
              Unable to load matches. Please check your connection.
            </Text>
            <Button mode="contained" onPress={() => refetch()} style={{ marginTop: 16 }}>
              Retry
            </Button>
          </View>
        ) : isLoading ? (
          <ActivityIndicator size="large" color="#3B82F6" style={{ marginTop: 40 }} />
        ) : filteredMatchGroups.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>No matches found</Text>
          </View>
        ) : (
          filteredMatchGroups.map((group: any, index: number) => (
            <View key={index} style={styles.leagueSection}>
              <View style={styles.leagueHeader}>
                <Text style={styles.leagueName}>{group.league.name}</Text>
                <Text style={styles.leagueCountry}>{group.league.country}</Text>
              </View>

              {group.matches.map((match: Match) => (
                <CompactMatchCard
                  key={match.id}
                  match={match}
                  onPress={() => navigation.navigate('MatchDetail', { matchId: match.id })}
                />
              ))}
            </View>
          ))
        )}
      </ScrollView>
    </View>
  );
}

// --- Components ---

function NotificationPopup({ visible, onClose, notifications }: { visible: boolean; onClose: () => void; notifications: AppNotification[] }) {
  const navigation = useNavigation<NavigationProp>();

  if (!visible) return null;

  return (
    <View style={styles.popupOverlay}>
      <TouchableOpacity style={styles.popupBackdrop} onPress={onClose} activeOpacity={1} />
      <Surface style={styles.popupContainer} elevation={4}>
        <View style={styles.popupHeader}>
          <Text style={styles.popupTitle}>Notifications</Text>
          <IconButton icon="close" size={20} onPress={onClose} />
        </View>

        {notifications.length === 0 ? (
          <View style={styles.popupEmpty}>
            <Text style={styles.popupEmptyText}>No notifications</Text>
          </View>
        ) : (
          <FlatList
            data={notifications}
            keyExtractor={item => item.id}
            style={{ maxHeight: 300 }}
            renderItem={({ item }) => {
              let icon = 'information';
              let color = '#3B82F6';
              switch (item.type) {
                case 'MATCH_START': icon = 'clock-outline'; color = '#F59E0B'; break;
                case 'GOAL': icon = 'soccer'; color = '#22C55E'; break;
                case 'MATCH_END': icon = 'flag-checkered'; color = '#EF4444'; break;
              }
              return (
                <TouchableOpacity
                  style={styles.popupItem}
                  onPress={() => {
                    onClose();
                    if (item.matchId) navigation.navigate('MatchDetail', { matchId: item.matchId });
                  }}
                >
                  <View style={[styles.popupIcon, { backgroundColor: `${color}20` }]}>
                    <Icon name={icon} size={16} color={color} />
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.popupItemTitle}>{item.title}</Text>
                    <Text style={styles.popupItemMessage} numberOfLines={2}>{item.message}</Text>
                    <Text style={styles.popupItemTime}>{formatDistanceToNow(item.time, { addSuffix: true })}</Text>
                  </View>
                </TouchableOpacity>
              );
            }}
          />
        )}
      </Surface>
    </View>
  );
}

function FeaturedMatchCard({ match, onPress }: { match: Match; onPress: () => void }) {
  const isLive = match.status === 'live';

  // Fetch prediction
  const { data: predictionData } = useQuery({
    queryKey: ['prediction', match.id],
    queryFn: () => MatchService.getMatchPrediction(match.id),
    enabled: !!match.id,
    staleTime: 300000, // 5 mins
  });
  const prediction = predictionData?.data;

  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.9}>
      <LinearGradient
        colors={['#3B82F6', '#2563EB']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.featuredCard}
      >
        <View style={styles.featuredHeader}>
          <View>
            <Text style={styles.featuredLeague}>{match.league.name}</Text>
            {prediction && (
              <View style={styles.predictionBadge}>
                <Text style={styles.predictionText}>
                  AI: {prediction.predictedScore.home}-{prediction.predictedScore.away}
                </Text>
              </View>
            )}
          </View>
          {isLive ? (
            <View style={styles.liveTag}>
              <View style={styles.liveDot} />
              <Text style={styles.liveText}>LIVE</Text>
            </View>
          ) : (
            <Text style={styles.matchTime}>{format(new Date(match.matchDate), 'HH:mm')}</Text>
          )}
        </View>

        <View style={styles.featuredContent}>
          <View style={styles.teamCol}>
            <View style={styles.teamLogoContainer}>
              {match.homeTeam.logo ? (
                <Image source={{ uri: match.homeTeam.logo }} style={styles.teamLogo} resizeMode="contain" />
              ) : (
                <View style={styles.teamLogoPlaceholder}>
                  <Text style={styles.teamLogoText}>{match.homeTeam.name.charAt(0)}</Text>
                </View>
              )}
            </View>
            <Text style={styles.featuredTeamName} numberOfLines={2}>{match.homeTeam.name}</Text>
          </View>

          <View style={styles.scoreCol}>
            <Text style={styles.featuredScore}>
              {match.homeScore === null ? 'VS' : `${match.homeScore} - ${match.awayScore}`}
            </Text>
            {prediction && (
              <View style={styles.winProbBar}>
                {/* Simple Visual Bar */}
                <View style={{ flexDirection: 'row', height: 4, width: '100%', borderRadius: 2, overflow: 'hidden', marginTop: 8 }}>
                  <View style={{ flex: prediction.homeWinProbability, backgroundColor: '#60A5FA' }} />
                  <View style={{ flex: prediction.drawProbability, backgroundColor: '#94A3B8' }} />
                  <View style={{ flex: prediction.awayWinProbability, backgroundColor: '#F87171' }} />
                </View>
                <Text style={{ color: '#BFDBFE', fontSize: 10, marginTop: 4 }}>
                  Tỉ lệ thắng: {(prediction.homeWinProbability * 100).toFixed(0)}%
                </Text>
              </View>
            )}
          </View>

          <View style={styles.teamCol}>
            <View style={styles.teamLogoContainer}>
              {match.awayTeam.logo ? (
                <Image source={{ uri: match.awayTeam.logo }} style={styles.teamLogo} resizeMode="contain" />
              ) : (
                <View style={styles.teamLogoPlaceholder}>
                  <Text style={styles.teamLogoText}>{match.awayTeam.name.charAt(0)}</Text>
                </View>
              )}
            </View>
            <Text style={styles.featuredTeamName} numberOfLines={2}>{match.awayTeam.name}</Text>
          </View>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );
}

function CompactMatchCard({ match, onPress }: { match: Match; onPress: () => void }) {
  const isLive = match.status === 'live';

  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.7}>
      <View style={styles.matchCard}>
        <View style={styles.matchInfo}>
          <Text style={styles.matchTimeSmall}>
            {isLive ? 'LIVE' : format(new Date(match.matchDate), 'HH:mm')}
          </Text>
          {isLive && <View style={styles.liveDotSmall} />}
        </View>

        <View style={styles.matchTeams}>
          <View style={styles.teamRow}>
            <View style={styles.teamNameContainer}>
              {match.homeTeam.logo ? (
                <Image source={{ uri: match.homeTeam.logo }} style={styles.teamLogoSmall} resizeMode="contain" />
              ) : null}
              <Text style={[styles.teamNameSmall, isLive && styles.teamNameLive]}>
                {match.homeTeam.name}
              </Text>
            </View>
            <Text style={[styles.scoreSmall, isLive && styles.scoreLive]}>
              {match.homeScore === null ? '-' : match.homeScore}
            </Text>
          </View>
          <View style={styles.teamRow}>
            <View style={styles.teamNameContainer}>
              {match.awayTeam.logo ? (
                <Image source={{ uri: match.awayTeam.logo }} style={styles.teamLogoSmall} resizeMode="contain" />
              ) : null}
              <Text style={[styles.teamNameSmall, isLive && styles.teamNameLive]}>
                {match.awayTeam.name}
              </Text>
            </View>
            <Text style={[styles.scoreSmall, isLive && styles.scoreLive]}>
              {match.awayScore === null ? '-' : match.awayScore}
            </Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: Platform.OS === 'android' ? 10 : 20, // Reduced padding
    paddingBottom: 10,
    zIndex: 10, // Ensure header is above content for popup context if needed
  },
  logo: {
    width: 200, // Increased size
    height: 60,
  },
  iconButton: {
    position: 'relative',
  },
  badge: {
    position: 'absolute',
    top: 5,
    right: 5,
    backgroundColor: '#EF4444',
  },
  // Popup Styles
  popupOverlay: {
    position: 'absolute',
    top: 80, // adjust based on header height
    right: 10,
    width: 320,
    zIndex: 1000,
  },
  popupBackdrop: {
    position: 'absolute',
    top: -1000, // Cover entire screen
    left: -1000,
    right: -1000,
    bottom: -1000,
  },
  popupContainer: {
    backgroundColor: '#1E293B',
    borderRadius: 12,
    overflow: 'hidden',
  },
  popupHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
  },
  popupTitle: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  popupEmpty: {
    padding: 20,
    alignItems: 'center',
  },
  popupEmptyText: {
    color: '#94A3B8',
  },
  popupItem: {
    flexDirection: 'row',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  popupIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  popupItemTitle: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
    marginBottom: 2,
  },
  popupItemMessage: {
    color: '#CBD5E1',
    fontSize: 12,
    marginBottom: 4,
  },
  popupItemTime: {
    color: '#64748B',
    fontSize: 10,
  },

  dateStripWrapper: {
    marginBottom: 20,
  },
  dateStripContent: {
    paddingHorizontal: 14,
  },
  dateItem: {
    width: 50,
    height: 70,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 6,
    borderRadius: 16,
    backgroundColor: 'rgba(30, 41, 59, 0.5)', // Glassy effect
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  dateItemSelected: {
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
  },
  dayName: {
    fontSize: 12,
    marginBottom: 4,
    fontWeight: '500',
  },
  dayNumber: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  textSelected: {
    color: '#fff',
  },
  textUnselected: {
    color: '#94A3B8',
  },
  todayDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#3B82F6',
    marginTop: 4,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 100,
  },
  featuredSection: {
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  featuredCard: {
    borderRadius: 24,
    padding: 20,
    shadowColor: '#3B82F6',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  featuredHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  featuredLeague: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  matchTime: {
    color: '#fff',
    fontWeight: 'bold',
  },
  liveTag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  liveDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#EF4444',
    marginRight: 4,
  },
  liveText: {
    color: '#EF4444',
    fontSize: 10,
    fontWeight: 'bold',
  },
  featuredContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  teamCol: {
    alignItems: 'center',
    width: '35%',
  },
  teamLogoContainer: {
    width: 60,
    height: 60,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  teamLogo: {
    width: 50,
    height: 50,
  },
  teamLogoPlaceholder: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  teamLogoText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  featuredTeamName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  scoreCol: {
    width: '30%',
    alignItems: 'center',
  },
  featuredScore: {
    color: '#fff',
    fontSize: 32,
    fontWeight: 'bold',
  },
  searchbar: {
    marginHorizontal: 20,
    marginBottom: 24,
    backgroundColor: 'rgba(30, 41, 59, 0.5)',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    height: 50,
  },
  searchInput: {
    color: '#fff',
  },
  leagueSection: {
    marginBottom: 20,
    paddingHorizontal: 20,
  },
  leagueHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  leagueName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 8,
  },
  leagueCountry: {
    color: '#94A3B8',
    fontSize: 12,
  },
  matchCard: {
    flexDirection: 'row',
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  matchInfo: {
    width: 60,
    borderRightWidth: 1,
    borderRightColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  matchTimeSmall: {
    color: '#94A3B8',
    fontSize: 12,
    fontWeight: '600',
  },
  liveDotSmall: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#EF4444',
    marginTop: 4,
  },
  matchTeams: {
    flex: 1,
    justifyContent: 'center',
  },
  teamRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  teamNameContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  teamLogoSmall: {
    width: 20,
    height: 20,
    marginRight: 8,
  },
  teamNameSmall: {
    color: '#CBD5E1',
    fontSize: 14,
    fontWeight: '500',
    flex: 1,
  },
  teamNameLive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  scoreSmall: {
    color: '#CBD5E1',
    fontSize: 14,
    fontWeight: '600',
  },
  scoreLive: {
    color: '#3B82F6',
    fontWeight: 'bold',
  },
  emptyState: {
    alignItems: 'center',
    marginTop: 40,
  },
  emptyText: {
    color: '#94A3B8',
    fontSize: 16,
  },
  predictionBadge: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    marginTop: 4,
    alignSelf: 'flex-start'
  },
  predictionText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold'
  },
  winProbBar: {
    width: '100%',
    alignItems: 'center',
    marginTop: 8
  }
});
