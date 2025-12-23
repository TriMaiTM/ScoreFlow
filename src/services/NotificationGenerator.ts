
import { Match, UserProfile } from '../types';
import { differenceInMinutes, isAfter, isBefore, subHours } from 'date-fns';

export interface AppNotification {
    id: string;
    type: 'MATCH_START' | 'GOAL' | 'MATCH_END' | 'INFO';
    title: string;
    message: string;
    time: Date;
    read: boolean;
    matchId?: number;
}

export class NotificationGenerator {
    static generateNotifications(matches: Match[], profile: UserProfile | null): AppNotification[] {
        if (!profile || !profile.notificationSettings.enabled) return [];

        const notifications: AppNotification[] = [];
        const settings = profile.notificationSettings;
        const favorites = profile.favoriteTeams || [];

        matches.forEach(match => {
            // Filter by favorites if enabled
            if (settings.favoriteTeamsOnly) {
                if (!favorites.includes(match.homeTeam.id) && !favorites.includes(match.awayTeam.id)) {
                    return;
                }
            }

            const matchTime = new Date(match.matchDate);
            const now = new Date();

            // 1. Match Start (30 min before)
            if (settings.matchStart) {
                const diff = differenceInMinutes(matchTime, now);
                // Show if match starts in 0-30 mins OR started less than 30 mins ago
                if (diff > -30 && diff <= 30) {
                    notifications.push({
                        id: `start_${match.id}`,
                        type: 'MATCH_START',
                        title: 'Match Starting Soon',
                        message: `${match.homeTeam.name} vs ${match.awayTeam.name} starts in ${Math.max(0, diff)} minutes!`,
                        time: new Date(matchTime.getTime() - 30 * 60000), // 30 mins before
                        read: false,
                        matchId: match.id
                    });
                }
            }

            // 2. Goals / Live Score Updates
            if (settings.goals && match.status === 'live') {
                // Mocking goals based on score availability
                // In a real app, this would come from a socket or diffing state
                const homeScore = match.homeScore ?? 0;
                const awayScore = match.awayScore ?? 0;

                if (homeScore > 0 || awayScore > 0) {
                    notifications.push({
                        id: `goal_${match.id}_${homeScore}_${awayScore}`,
                        type: 'GOAL',
                        title: 'Goal Update ⚽',
                        message: `${match.homeTeam.name} ${homeScore} - ${awayScore} ${match.awayTeam.name}`,
                        time: now, // Just show as "now" for mock
                        read: false,
                        matchId: match.id
                    });
                }
            }

            // 3. Match End
            if (settings.matchEnd && match.status === 'finished') {
                // Show if finished within last 2 hours
                // Assuming we can infer finish time or just look at past matches
                if (differenceInMinutes(now, matchTime) < 150 && differenceInMinutes(now, matchTime) > 90) {
                    notifications.push({
                        id: `end_${match.id}`,
                        type: 'MATCH_END',
                        title: 'Full Time 🏁',
                        message: `Match Ended: ${match.homeTeam.name} ${match.homeScore} - ${match.awayScore} ${match.awayTeam.name}`,
                        time: new Date(matchTime.getTime() + 105 * 60000), // Roughly 105 mins after start
                        read: false,
                        matchId: match.id
                    });
                }
            }
        });

        // Sort by time (newest first)
        return notifications.sort((a, b) => b.time.getTime() - a.time.getTime());
    }
}
