// Core types for ScoreFlow application

export interface Team {
  id: number;
  name: string;
  shortName: string;
  logo: string;
  country: string;
}

export interface Match {
  id: number;
  homeTeam: Team;
  awayTeam: Team;
  matchDate: string;
  status: 'scheduled' | 'live' | 'finished' | 'postponed' | 'cancelled';
  homeScore: number | null;
  awayScore: number | null;
  league: League;
  venue: string;
  round?: string;
}

export interface League {
  id: number;
  name: string;
  country: string;
  logo: string;
  season: number;
}

export interface Standing {
  position: number;
  team: Team;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goalsFor: number;
  goalsAgainst: number;
  goalDifference: number;
  points: number;
  form: string; // e.g., "WWDWL"
}

export interface Player {
  id: number;
  name: string;
  position: string;
  number: number;
  photo: string;
  nationality: string;
  age: number;
}

export interface TeamStats {
  teamId: number;
  form: string; // Last 5 matches: W/D/L
  goalsScored: number;
  goalsConceded: number;
  cleanSheets: number;
  avgGoalsScored: number;
  avgGoalsConceded: number;
  homeWinPercentage: number;
  awayWinPercentage: number;
}

export interface HeadToHead {
  matches: Match[];
  homeTeamWins: number;
  awayTeamWins: number;
  draws: number;
}

export interface Prediction {
  matchId: number;
  homeWinProbability: number;
  drawProbability: number;
  awayWinProbability: number;
  predictedScore: {
    home: number;
    away: number;
  };
  confidence: number; // 0-1
  features: PredictionFeatures;
}

export interface PredictionFeatures {
  homeTeamElo: number;
  awayTeamElo: number;
  homeForm: number;
  awayForm: number;
  homeGoalsAvg: number;
  awayGoalsAvg: number;
  h2hHomeWins: number;
  h2hAwayWins: number;
  h2hDraws: number;
  isHomeMatch: boolean;
  daysSinceLastMatch: {
    home: number;
    away: number;
  };
  injuredPlayers: {
    home: number;
    away: number;
  };
}

export interface Injury {
  player: Player;
  reason: string;
  expectedReturn: string | null;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  favoriteTeams: number[];
  favoriteLeagues: number[];
  followedMatches: number[];
  notificationSettings: NotificationSettings;
}

export interface NotificationSettings {
  enabled: boolean;
  matchStart: boolean; // 30 min before
  goals: boolean;
  matchEnd: boolean;
  favoriteTeamsOnly: boolean;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  page: number;
  totalPages: number;
  totalItems: number;
}

export type MatchFilter = {
  leagueId?: number;
  teamId?: number;
  status?: Match['status'];
  dateFrom?: string;
  dateTo?: string;
};
