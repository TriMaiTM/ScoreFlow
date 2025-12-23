import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, Image, Platform, StatusBar, TouchableOpacity } from 'react-native';
import { Text, ActivityIndicator, Surface, Menu, Button, Provider } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { LinearGradient } from 'expo-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { LeagueService } from '../services/MatchService';

export default function StandingsScreen() {
  const [selectedLeagueId, setSelectedLeagueId] = useState(2021); // Premier League
  const [menuVisible, setMenuVisible] = useState(false);

  const { data: leaguesData } = useQuery({
    queryKey: ['leagues'],
    queryFn: () => LeagueService.getLeagues(),
  });

  const { data: standingsData, isLoading } = useQuery({
    queryKey: ['standings', selectedLeagueId],
    queryFn: () => LeagueService.getStandings(selectedLeagueId),
    enabled: !!selectedLeagueId,
  });

  const leagues = leaguesData?.data || [];
  const standings = standingsData?.data || [];

  const selectedLeague = leagues.find((l: any) => l.id === selectedLeagueId);

  const openMenu = () => setMenuVisible(true);
  const closeMenu = () => setMenuVisible(false);

  const handleLeagueSelect = (id: number) => {
    setSelectedLeagueId(id);
    closeMenu();
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
        <Text style={styles.headerTitle}>Bảng xếp hạng</Text>
      </View>

      {/* League Selector */}
      <View style={styles.selectorContainer}>
        <Menu
          visible={menuVisible}
          onDismiss={closeMenu}
          anchor={
            <TouchableOpacity onPress={openMenu}>
              <Surface style={styles.pickerWrapper} elevation={2}>
                <Text style={styles.pickerText}>
                  {selectedLeague ? selectedLeague.name : 'Chọn giải đấu'}
                </Text>
                <Icon name="chevron-down" size={24} color="#fff" />
              </Surface>
            </TouchableOpacity>
          }
          contentStyle={styles.menuContent}
        >
          {leagues.map((league: any) => (
            <Menu.Item
              key={league.id}
              onPress={() => handleLeagueSelect(league.id)}
              title={league.name}
              titleStyle={{ color: '#fff' }}
              style={styles.menuItem}
            />
          ))}
        </Menu>
      </View>

      {isLoading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#3B82F6" />
        </View>
      ) : (
        <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
          <Surface style={styles.tableCard} elevation={1}>
            {/* Table Header */}
            <View style={styles.tableHeader}>
              <Text style={[styles.colPos, styles.headerText]}>#</Text>
              <Text style={[styles.colTeam, styles.headerText]}>Team</Text>
              <Text style={[styles.colStat, styles.headerText]}>P</Text>
              <Text style={[styles.colStat, styles.headerText]}>W</Text>
              <Text style={[styles.colStat, styles.headerText]}>D</Text>
              <Text style={[styles.colStat, styles.headerText]}>L</Text>
              <Text style={[styles.colStat, styles.headerText]}>GD</Text>
              <Text style={[styles.colPts, styles.headerText]}>Pts</Text>
            </View>

            {/* Table Rows */}
            {standings.map((standing: any, index: number) => (
              <View key={standing.position} style={[
                styles.tableRow,
                index % 2 === 0 ? styles.rowEven : styles.rowOdd,
                index === standings.length - 1 && styles.lastRow
              ]}>
                <Text style={[styles.colPos, styles.rowText]}>{standing.position}</Text>

                <View style={styles.colTeam}>
                  <View style={styles.teamInfo}>
                    {standing.team.logo ? (
                      <Image source={{ uri: standing.team.logo }} style={styles.teamLogo} resizeMode="contain" />
                    ) : (
                      <View style={styles.logoPlaceholder}>
                        <Text style={styles.logoPlaceholderText}>{standing.team.name.charAt(0)}</Text>
                      </View>
                    )}
                    <Text style={[styles.teamName, styles.rowText]} numberOfLines={1}>
                      {standing.team.name}
                    </Text>
                  </View>
                </View>

                <Text style={[styles.colStat, styles.rowText]}>{standing.played}</Text>
                <Text style={[styles.colStat, styles.rowText]}>{standing.won}</Text>
                <Text style={[styles.colStat, styles.rowText]}>{standing.drawn}</Text>
                <Text style={[styles.colStat, styles.rowText]}>{standing.lost}</Text>
                <Text style={[styles.colStat, styles.rowText]}>
                  {standing.goalDifference > 0 ? `+${standing.goalDifference}` : standing.goalDifference}
                </Text>
                <Text style={[styles.colPts, styles.ptsText]}>{standing.points}</Text>
              </View>
            ))}
          </Surface>
        </ScrollView>
      )}
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
  selectorContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
    zIndex: 100, // Ensure menu is on top
  },
  pickerWrapper: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'rgba(30, 41, 59, 0.6)',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  pickerText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
  },
  menuContent: {
    backgroundColor: '#1E293B',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    marginTop: 40, // Adjust position if needed
  },
  menuItem: {
    maxWidth: 300,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
    zIndex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  tableCard: {
    backgroundColor: 'rgba(30, 41, 59, 0.6)',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
    overflow: 'hidden',
  },
  tableHeader: {
    flexDirection: 'row',
    paddingVertical: 12,
    paddingHorizontal: 12,
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
  },
  headerText: {
    color: '#94A3B8',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  tableRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  lastRow: {
    borderBottomWidth: 0,
  },
  rowEven: {
    backgroundColor: 'transparent',
  },
  rowOdd: {
    backgroundColor: 'rgba(255,255,255,0.02)',
  },
  rowText: {
    color: '#CBD5E1',
    fontSize: 13,
    textAlign: 'center',
  },
  ptsText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
    textAlign: 'center',
  },

  // Columns
  colPos: {
    width: 30,
    textAlign: 'center',
  },
  colTeam: {
    flex: 1,
    paddingLeft: 8,
    alignItems: 'flex-start',
  },
  colStat: {
    width: 30,
  },
  colPts: {
    width: 35,
  },

  // Team Info
  teamInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  teamLogo: {
    width: 20,
    height: 20,
    marginRight: 8,
  },
  logoPlaceholder: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  logoPlaceholderText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  teamName: {
    textAlign: 'left',
  },
});
