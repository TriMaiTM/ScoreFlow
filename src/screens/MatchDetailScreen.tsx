import React from 'react';
import { View, ScrollView, StyleSheet, Image, Dimensions, Platform, StatusBar } from 'react-native';
import { Text, ActivityIndicator, Chip, Divider, IconButton, Surface } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';
import { format } from 'date-fns';
import { LinearGradient } from 'expo-linear-gradient';

import { MatchService, TeamService } from '../services/MatchService';
import { RootStackParamList } from '../navigation/AppNavigator';
import { CacheService } from '../services/CacheService';
import { Match } from '../types';

type MatchDetailRouteProp = RouteProp<RootStackParamList, 'MatchDetail'>;

const { width } = Dimensions.get('window');

export default function MatchDetailScreen() {
  const route = useRoute<MatchDetailRouteProp>();
  const navigation = useNavigation();
  const { matchId } = route.params;

  const { data: matchData, isLoading: matchLoading } = useQuery({
    queryKey: ['match', matchId],
    queryFn: async () => {
      const isOnline = await CacheService.isOnline();
      if (!isOnline) {
        const cached = await CacheService.get(`match_${matchId}`);
        if (cached) return { data: cached, success: true };
      }
      const response = await MatchService.getMatchById(matchId);
      if (response.success) {
        await CacheService.set(`match_${matchId}`, response.data);
      }
      return response;
    },
  });

  const { data: predictionData, isLoading: predictionLoading } = useQuery({
    queryKey: ['prediction', matchId],
    queryFn: async () => {
      const response = await MatchService.getMatchPrediction(matchId);
      return response;
    },
  });

  const match = matchData?.data as Match | undefined;
  const prediction = predictionData?.data;

  // Fetch H2H data
  const { data: h2hData } = useQuery({
    queryKey: ['h2h', match?.homeTeam?.id, match?.awayTeam?.id],
    queryFn: async () => {
      if (!match) return null;
      const response = await MatchService.getHeadToHeadDetailed(
        match.homeTeam.id,
        match.awayTeam.id,
        5
      );
      return response;
    },
    enabled: !!match,
  });

  // Fetch recent matches for both teams
  const { data: homeRecentMatches } = useQuery({
    queryKey: ['recentMatches', match?.homeTeam?.id],
    queryFn: async () => {
      if (!match) return null;
      const response = await TeamService.getTeamRecentMatches(match.homeTeam.id, 5);
      return response;
    },
    enabled: !!match,
  });

  const { data: awayRecentMatches } = useQuery({
    queryKey: ['recentMatches', match?.awayTeam?.id],
    queryFn: async () => {
      if (!match) return null;
      const response = await TeamService.getTeamRecentMatches(match.awayTeam.id, 5);
      return response;
    },
    enabled: !!match,
  });

  const h2hMatches = h2hData?.data || [];
  const homeRecent = homeRecentMatches?.data || [];
  const awayRecent = awayRecentMatches?.data || [];

  if (matchLoading) {
    return (
      <View style={styles.centerContainer}>
        <StatusBar barStyle="light-content" backgroundColor="#0F172A" />
        <LinearGradient
          colors={['#0F172A', '#1E293B', '#0F172A']}
          style={StyleSheet.absoluteFill}
        />
        <ActivityIndicator size="large" color="#3B82F6" />
      </View>
    );
  }

  if (!match) {
    return (
      <View style={styles.centerContainer}>
        <StatusBar barStyle="light-content" backgroundColor="#0F172A" />
        <LinearGradient
          colors={['#0F172A', '#1E293B', '#0F172A']}
          style={StyleSheet.absoluteFill}
        />
        <Text style={{ color: '#fff' }}>Match not found</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0F172A" />
      <LinearGradient
        colors={['#0F172A', '#1E293B', '#0F172A']}
        style={StyleSheet.absoluteFill}
      />

      {/* Header */}
      <View style={styles.header}>
        <IconButton icon="arrow-left" iconColor="#fff" onPress={() => navigation.goBack()} />
        <Text style={styles.headerTitle}>Match Details</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Match Header Card */}
        <Surface style={styles.matchCard} elevation={2}>
          <Text style={styles.leagueName}>{match.league.name}</Text>
          <Text style={styles.matchDate}>
            {format(new Date(match.matchDate), 'PPpp')}
          </Text>
          <Text style={styles.venue}>📍 {match.venue}</Text>

          <View style={styles.scoreContainer}>
            <View style={styles.teamSection}>
              <View style={styles.logoContainer}>
                {match.homeTeam.logo ? (
                  <Image source={{ uri: match.homeTeam.logo }} style={styles.teamLogo} resizeMode="contain" />
                ) : (
                  <View style={styles.logoPlaceholder}>
                    <Text style={styles.logoPlaceholderText}>{match.homeTeam.name.charAt(0)}</Text>
                  </View>
                )}
              </View>
              <Text style={styles.teamName} numberOfLines={2}>{match.homeTeam.name}</Text>
            </View>

            <View style={styles.scoreBoard}>
              {match.status === 'scheduled' ? (
                <Text style={styles.vsText}>VS</Text>
              ) : (
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                  <Text style={styles.score}>{match.homeScore}</Text>
                  <Text style={styles.scoreDivider}>-</Text>
                  <Text style={styles.score}>{match.awayScore}</Text>
                </View>
              )}
              {match.status === 'live' && (
                <View style={styles.liveTag}>
                  <View style={styles.liveDot} />
                  <Text style={styles.liveText}>LIVE</Text>
                </View>
              )}
            </View>

            <View style={styles.teamSection}>
              <View style={styles.logoContainer}>
                {match.awayTeam.logo ? (
                  <Image source={{ uri: match.awayTeam.logo }} style={styles.teamLogo} resizeMode="contain" />
                ) : (
                  <View style={styles.logoPlaceholder}>
                    <Text style={styles.logoPlaceholderText}>{match.awayTeam.name.charAt(0)}</Text>
                  </View>
                )}
              </View>
              <Text style={styles.teamName} numberOfLines={2}>{match.awayTeam.name}</Text>
            </View>
          </View>
        </Surface>

        {/* AI Prediction */}
        {prediction && (
          <Surface style={styles.sectionCard} elevation={1}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>🔮 AI Prediction</Text>
            </View>

            <View style={styles.predictionContent}>
              <View style={styles.predictionRow}>
                <ProbabilityBar
                  label={`${match.homeTeam.shortName}`}
                  probability={prediction.homeWinProbability}
                  color="#3B82F6"
                />
                <ProbabilityBar
                  label="Draw"
                  probability={prediction.drawProbability}
                  color="#94A3B8"
                />
                <ProbabilityBar
                  label={`${match.awayTeam.shortName}`}
                  probability={prediction.awayWinProbability}
                  color="#EF4444"
                />
              </View>

              <Divider style={styles.divider} />

              <View style={styles.predictionResult}>
                <View>
                  <Text style={styles.predictionLabel}>Predicted Score</Text>
                  <Text style={styles.predictedScoreValue}>
                    {prediction.predictedScore.home} - {prediction.predictedScore.away}
                  </Text>
                </View>
                <View>
                  <Text style={styles.predictionLabel}>Confidence</Text>
                  <Text style={styles.confidenceValue}>
                    {(prediction.confidence * 100).toFixed(0)}%
                  </Text>
                </View>
              </View>
            </View>
          </Surface>
        )}

        {/* Recent Form */}
        <Surface style={styles.sectionCard} elevation={1}>
          <Text style={styles.sectionTitle}>📈 Recent Form</Text>

          <View style={styles.formContainer}>
            {/* Home Team */}
            <View style={styles.teamFormColumn}>
              <View style={styles.formTeamHeader}>
                {match.homeTeam.logo && (
                  <Image source={{ uri: match.homeTeam.logo }} style={styles.smallLogo} />
                )}
                <Text style={styles.formTeamName}>{match.homeTeam.shortName}</Text>
              </View>
              {homeRecent.length > 0 ? (
                homeRecent.map((m: any, i: number) => (
                  <FormItem key={i} match={m} />
                ))
              ) : (
                <Text style={styles.noDataText}>No data</Text>
              )}
            </View>

            <View style={styles.verticalDivider} />

            {/* Away Team */}
            <View style={styles.teamFormColumn}>
              <View style={styles.formTeamHeader}>
                {match.awayTeam.logo && (
                  <Image source={{ uri: match.awayTeam.logo }} style={styles.smallLogo} />
                )}
                <Text style={styles.formTeamName}>{match.awayTeam.shortName}</Text>
              </View>
              {awayRecent.length > 0 ? (
                awayRecent.map((m: any, i: number) => (
                  <FormItem key={i} match={m} />
                ))
              ) : (
                <Text style={styles.noDataText}>No data</Text>
              )}
            </View>
          </View>
        </Surface>

        {/* Head-to-Head */}
        {h2hMatches.length > 0 && (
          <Surface style={styles.sectionCard} elevation={1}>
            <Text style={styles.sectionTitle}>🔄 Head-to-Head</Text>
            {h2hMatches.map((h2hMatch: any, index: number) => (
              <View key={index} style={styles.h2hItem}>
                <View style={styles.h2hRow}>
                  <Text style={[styles.h2hTeam, { textAlign: 'right' }]}>{h2hMatch.homeTeam.name}</Text>
                  <View style={styles.h2hScoreContainer}>
                    <Text style={styles.h2hScore}>
                      {h2hMatch.score.home} - {h2hMatch.score.away}
                    </Text>
                  </View>
                  <Text style={[styles.h2hTeam, { textAlign: 'left' }]}>{h2hMatch.awayTeam.name}</Text>
                </View>
                <Text style={styles.h2hDate}>{format(new Date(h2hMatch.date), 'PP')}</Text>
                {index < h2hMatches.length - 1 && <Divider style={styles.divider} />}
              </View>
            ))}
          </Surface>
        )}
      </ScrollView>
    </View>
  );
}

// --- Sub-components ---

function ProbabilityBar({ label, probability, color }: { label: string; probability: number; color: string }) {
  return (
    <View style={styles.probItem}>
      <View style={styles.probBarContainer}>
        <View style={[styles.probBar, { height: `${probability * 100}%`, backgroundColor: color }]} />
      </View>
      <Text style={styles.probValue}>{(probability * 100).toFixed(0)}%</Text>
      <Text style={styles.probLabel} numberOfLines={1}>{label}</Text>
    </View>
  );
}

function FormItem({ match }: { match: any }) {
  const getResultColor = (result: string) => {
    switch (result) {
      case 'W': return '#22C55E';
      case 'D': return '#EAB308';
      case 'L': return '#EF4444';
      default: return '#94A3B8';
    }
  };

  return (
    <View style={styles.formItem}>
      <View style={[styles.resultBadge, { backgroundColor: getResultColor(match.result) }]}>
        <Text style={styles.resultText}>{match.result}</Text>
      </View>
      <Text style={styles.formScore}>{match.teamScore}-{match.opponentScore}</Text>
      <Text style={styles.formOpponent} numberOfLines={1}>vs {match.opponent.shortName}</Text>
    </View>
  );
}

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
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: Platform.OS === 'android' ? 40 : 60,
    paddingBottom: 10,
    paddingHorizontal: 10,
  },
  headerTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  matchCard: {
    backgroundColor: 'rgba(30, 41, 59, 0.6)',
    borderRadius: 24,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  leagueName: {
    color: '#94A3B8',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 4,
    textTransform: 'uppercase',
    fontWeight: '600',
  },
  matchDate: {
    color: '#fff',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 4,
  },
  venue: {
    color: '#64748B',
    fontSize: 12,
    textAlign: 'center',
    marginBottom: 20,
  },
  scoreContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  teamSection: {
    flex: 1,
    alignItems: 'center',
  },
  logoContainer: {
    width: 80,
    height: 80,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 40,
  },
  teamLogo: {
    width: 60,
    height: 60,
  },
  logoPlaceholder: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#334155',
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoPlaceholderText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  teamName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  scoreBoard: {
    alignItems: 'center',
    marginHorizontal: 10,
  },
  score: {
    color: '#fff',
    fontSize: 36,
    fontWeight: 'bold',
  },
  scoreDivider: {
    color: '#64748B',
    fontSize: 36,
    marginHorizontal: 8,
  },
  vsText: {
    color: '#64748B',
    fontSize: 24,
    fontWeight: 'bold',
  },
  liveTag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 8,
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
  sectionCard: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  predictionContent: {
    paddingTop: 8,
  },
  predictionRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    height: 120,
    alignItems: 'flex-end',
    marginBottom: 16,
  },
  probItem: {
    alignItems: 'center',
    width: '30%',
  },
  probBarContainer: {
    height: 80,
    width: 8,
    backgroundColor: '#334155',
    borderRadius: 4,
    justifyContent: 'flex-end',
    marginBottom: 8,
    overflow: 'hidden',
  },
  probBar: {
    width: '100%',
    borderRadius: 4,
  },
  probValue: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  probLabel: {
    color: '#94A3B8',
    fontSize: 12,
  },
  divider: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    marginVertical: 16,
  },
  predictionResult: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  predictionLabel: {
    color: '#94A3B8',
    fontSize: 12,
    marginBottom: 4,
    textAlign: 'center',
  },
  predictedScoreValue: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  confidenceValue: {
    color: '#3B82F6',
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  formContainer: {
    flexDirection: 'row',
  },
  teamFormColumn: {
    flex: 1,
  },
  verticalDivider: {
    width: 1,
    backgroundColor: 'rgba(255,255,255,0.1)',
    marginHorizontal: 12,
  },
  formTeamHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    justifyContent: 'center',
  },
  smallLogo: {
    width: 20,
    height: 20,
    marginRight: 8,
  },
  formTeamName: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
  formItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    backgroundColor: 'rgba(255,255,255,0.03)',
    padding: 8,
    borderRadius: 8,
  },
  resultBadge: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  resultText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  formScore: {
    color: '#fff',
    fontWeight: 'bold',
    marginRight: 8,
    width: 30,
    textAlign: 'center',
  },
  formOpponent: {
    color: '#94A3B8',
    fontSize: 12,
    flex: 1,
  },
  noDataText: {
    color: '#64748B',
    textAlign: 'center',
    fontStyle: 'italic',
    marginTop: 10,
  },
  h2hItem: {
    marginBottom: 12,
  },
  h2hRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  h2hTeam: {
    color: '#CBD5E1',
    flex: 1,
    fontSize: 13,
  },
  h2hScoreContainer: {
    backgroundColor: '#334155',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    marginHorizontal: 8,
  },
  h2hScore: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12,
  },
  h2hDate: {
    color: '#64748B',
    fontSize: 11,
    textAlign: 'center',
  },
});