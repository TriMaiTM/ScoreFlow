import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  FlatList,
  Image,
  StatusBar,
  Platform,
} from 'react-native';
import { useQuery } from '@tanstack/react-query';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { format, addDays, isToday, parseISO } from 'date-fns';
import { LinearGradient } from 'expo-linear-gradient';

import { MatchService } from '../services/MatchService';
import { Match } from '../types';

interface LeagueGroup {
  league: {
    id: number;
    name: string;
    country: string;
    logo: string;
  };
  matches: Match[];
}

const MatchesScreen = ({ navigation }: any) => {
  // Date slider state
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [dateRange, setDateRange] = useState<Date[]>([]);
  const dateListRef = useRef<FlatList>(null);

  // Generate date range (yesterday to +14 days)
  useEffect(() => {
    const dates: Date[] = [];
    for (let i = -2; i <= 14; i++) {
      dates.push(addDays(new Date(), i));
    }
    setDateRange(dates);
  }, []);

  // Auto-scroll to selected date
  useEffect(() => {
    const index = dateRange.findIndex(
      (date) => format(date, 'yyyy-MM-dd') === format(selectedDate, 'yyyy-MM-dd')
    );
    if (index !== -1 && dateListRef.current) {
      dateListRef.current.scrollToIndex({ index, animated: true, viewPosition: 0.5 });
    }
  }, [selectedDate, dateRange]);

  // Fetch matches for selected date
  const {
    data: matchesData,
    isLoading,
    refetch,
    isRefetching,
  } = useQuery({
    queryKey: ['matchesByDate', format(selectedDate, 'yyyy-MM-dd')],
    queryFn: () => MatchService.getMatchesByDate(format(selectedDate, 'yyyy-MM-dd')),
    refetchInterval: 30000, // Auto-refetch every 30 seconds for real-time scores
  });

  const leagues = matchesData?.data?.leagues || [];
  const totalMatches = matchesData?.data?.totalMatches || 0;

  const renderDateItem = ({ item }: { item: Date }) => {
    const isSelected = format(item, 'yyyy-MM-dd') === format(selectedDate, 'yyyy-MM-dd');
    const isTodayDate = isToday(item);

    return (
      <TouchableOpacity
        style={[styles.dateItem, isSelected && styles.dateItemSelected]}
        onPress={() => setSelectedDate(item)}
      >
        <Text style={[styles.dateDayName, isSelected ? styles.textSelected : styles.textUnselected]}>
          {isTodayDate ? 'Today' : format(item, 'EEE')}
        </Text>
        <Text style={[styles.dateNumber, isSelected ? styles.textSelected : styles.textUnselected]}>
          {format(item, 'd')}
        </Text>
        {isTodayDate && !isSelected && <View style={styles.todayDot} />}
      </TouchableOpacity>
    );
  };

  const renderMatchCard = (match: Match) => {
    const isLive = match.status === 'live';
    const showScores = isLive || match.status === 'finished';

    return (
      <TouchableOpacity
        key={match.id}
        style={styles.matchCard}
        onPress={() => navigation.navigate('MatchDetail', { matchId: match.id })}
        activeOpacity={0.7}
      >
        <View style={styles.matchInfo}>
          <Text style={styles.matchTime}>
            {isLive ? 'LIVE' : format(new Date(match.matchDate), 'HH:mm')}
          </Text>
          {isLive && <View style={styles.liveDot} />}
        </View>

        <View style={styles.matchContent}>
          {/* Home Team */}
          <View style={styles.teamRow}>
            <View style={styles.teamNameContainer}>
              {match.homeTeam.logo ? (
                <Image source={{ uri: match.homeTeam.logo }} style={styles.teamLogo} resizeMode="contain" />
              ) : null}
              <Text style={[styles.teamName, isLive && styles.teamNameLive]}>
                {match.homeTeam.name}
              </Text>
            </View>
            {showScores && (
              <Text style={[styles.score, isLive && styles.scoreLive]}>
                {match.homeScore ?? '-'}
              </Text>
            )}
          </View>

          {/* Away Team */}
          <View style={styles.teamRow}>
            <View style={styles.teamNameContainer}>
              {match.awayTeam.logo ? (
                <Image source={{ uri: match.awayTeam.logo }} style={styles.teamLogo} resizeMode="contain" />
              ) : null}
              <Text style={[styles.teamName, isLive && styles.teamNameLive]}>
                {match.awayTeam.name}
              </Text>
            </View>
            {showScores && (
              <Text style={[styles.score, isLive && styles.scoreLive]}>
                {match.awayScore ?? '-'}
              </Text>
            )}
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  const renderLeagueSection = (leagueGroup: LeagueGroup) => (
    <View key={leagueGroup.league.id} style={styles.leagueSection}>
      <View style={styles.leagueHeader}>
        <Text style={styles.leagueName}>{leagueGroup.league.name}</Text>
        <Text style={styles.leagueCountry}>{leagueGroup.league.country}</Text>
      </View>
      {leagueGroup.matches.map((match) => renderMatchCard(match))}
    </View>
  );

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0F172A" />
      <LinearGradient
        colors={['#0F172A', '#1E293B', '#0F172A']}
        style={StyleSheet.absoluteFill}
      />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Matches</Text>
        <TouchableOpacity onPress={() => refetch()}>
          <Icon name="refresh" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      {/* Date Strip */}
      <View style={styles.dateStripWrapper}>
        <FlatList
          ref={dateListRef}
          data={dateRange}
          renderItem={renderDateItem}
          keyExtractor={(item) => item.toISOString()}
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.dateStripContent}
          getItemLayout={(data, index) => ({ length: 60, offset: 60 * index, index })}
        />
      </View>

      {/* Content */}
      {isLoading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#3B82F6" />
        </View>
      ) : (
        <ScrollView
          style={styles.matchesContainer}
          contentContainerStyle={styles.scrollContent}
          refreshControl={
            <RefreshControl refreshing={isRefetching} onRefresh={refetch} tintColor="#fff" />
          }
        >
          {leagues.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Icon name="soccer" size={64} color="rgba(255,255,255,0.2)" />
              <Text style={styles.emptyText}>No matches scheduled</Text>
              <Text style={styles.emptySubtext}>Select another date</Text>
            </View>
          ) : (
            leagues.map((leagueGroup) => renderLeagueSection(leagueGroup))
          )}
        </ScrollView>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: Platform.OS === 'android' ? 40 : 60,
    paddingBottom: 20,
  },
  headerTitle: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
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
    backgroundColor: 'rgba(30, 41, 59, 0.5)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  dateItemSelected: {
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
  },
  dateDayName: {
    fontSize: 12,
    marginBottom: 4,
    fontWeight: '500',
  },
  dateNumber: {
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
  matchesContainer: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 40,
  },
  leagueSection: {
    marginBottom: 24,
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
  matchTime: {
    color: '#94A3B8',
    fontSize: 12,
    fontWeight: '600',
  },
  liveDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#EF4444',
    marginTop: 4,
  },
  matchContent: {
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
  teamLogo: {
    width: 20,
    height: 20,
    marginRight: 8,
  },
  teamName: {
    color: '#CBD5E1',
    fontSize: 14,
    fontWeight: '500',
    flex: 1,
  },
  teamNameLive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  score: {
    color: '#CBD5E1',
    fontSize: 14,
    fontWeight: '600',
  },
  scoreLive: {
    color: '#3B82F6',
    fontWeight: 'bold',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 80,
  },
  emptyText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 16,
  },
  emptySubtext: {
    color: '#94A3B8',
    marginTop: 8,
  },
});

export default MatchesScreen;
