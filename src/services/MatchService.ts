import { apiClient } from './ApiClient';
import {
  Match,
  League,
  Standing,
  Team,
  HeadToHead,
  TeamStats,
  Prediction,
  MatchFilter,
  ApiResponse,
  PaginatedResponse,
} from '../types';

export class MatchService {
  static async getMatchesByDate(date: string): Promise<ApiResponse<any>> {
    return apiClient.get<ApiResponse<any>>(`/matches/by-date?date=${date}`);
  }

  static async getMatchesDateRange(
    dateFrom: string,
    dateTo: string,
    leagueId?: number
  ): Promise<ApiResponse<any>> {
    const params = new URLSearchParams({ date_from: dateFrom, date_to: dateTo });
    if (leagueId) params.append('league_id', leagueId.toString());
    return apiClient.get<ApiResponse<any>>(`/matches/date-range?${params.toString()}`);
  }

  static async getUpcomingMatches(
    filters?: MatchFilter
  ): Promise<ApiResponse<Match[]>> {
    const params = new URLSearchParams();
    if (filters?.leagueId) params.append('leagueId', filters.leagueId.toString());
    if (filters?.teamId) params.append('teamId', filters.teamId.toString());
    if (filters?.dateFrom) params.append('dateFrom', filters.dateFrom);
    if (filters?.dateTo) params.append('dateTo', filters.dateTo);

    return apiClient.get<ApiResponse<Match[]>>(`/matches/upcoming?${params.toString()}`);
  }

  static async getLiveMatches(): Promise<ApiResponse<Match[]>> {
    return apiClient.get<ApiResponse<Match[]>>('/matches/live');
  }

  static async getFinishedMatches(
    page: number = 1,
    limit: number = 20
  ): Promise<PaginatedResponse<Match>> {
    return apiClient.get<PaginatedResponse<Match>>(
      `/matches/finished?page=${page}&limit=${limit}`
    );
  }

  static async getMatchById(matchId: number): Promise<ApiResponse<Match>> {
    return apiClient.get<ApiResponse<Match>>(`/matches/${matchId}`);
  }

  static async getMatchPrediction(matchId: number): Promise<ApiResponse<Prediction>> {
    return apiClient.get<ApiResponse<Prediction>>(`/matches/${matchId}/prediction`);
  }

  static async getHeadToHead(
    homeTeamId: number,
    awayTeamId: number
  ): Promise<ApiResponse<HeadToHead>> {
    return apiClient.get<ApiResponse<HeadToHead>>(
      `/matches/h2h?homeTeam=${homeTeamId}&awayTeam=${awayTeamId}`
    );
  }

  static async getTeamStats(teamId: number): Promise<ApiResponse<TeamStats>> {
    return apiClient.get<ApiResponse<TeamStats>>(`/teams/${teamId}/stats`);
  }

  // Enhanced endpoints
  static async getHeadToHeadDetailed(
    team1Id: number,
    team2Id: number,
    last: number = 10
  ): Promise<ApiResponse<any[]>> {
    return apiClient.get<ApiResponse<any[]>>(
      `/enhanced/matches/h2h-detailed?team1_id=${team1Id}&team2_id=${team2Id}&last=${last}`
    );
  }

  static async getTeamStatisticsEnhanced(
    teamId: number,
    leagueId: number,
    season: number = 2024
  ): Promise<ApiResponse<any>> {
    return apiClient.get<ApiResponse<any>>(
      `/enhanced/teams/${teamId}/statistics?league_id=${leagueId}&season=${season}`
    );
  }

  static async getMatchStatistics(
    matchId: number,
    externalFixtureId?: number
  ): Promise<ApiResponse<any>> {
    const params = externalFixtureId ? `?external_fixture_id=${externalFixtureId}` : '';
    return apiClient.get<ApiResponse<any>>(
      `/enhanced/matches/${matchId}/statistics${params}`
    );
  }

  static async getTeamInjuries(
    teamId: number,
    leagueId: number,
    season: number = 2024
  ): Promise<ApiResponse<any[]>> {
    return apiClient.get<ApiResponse<any[]>>(
      `/enhanced/teams/${teamId}/injuries?league_id=${leagueId}&season=${season}`
    );
  }
}

export class LeagueService {
  static async getLeagues(): Promise<ApiResponse<League[]>> {
    return apiClient.get<ApiResponse<League[]>>('/leagues');
  }

  static async getLeagueById(leagueId: number): Promise<ApiResponse<League>> {
    return apiClient.get<ApiResponse<League>>(`/leagues/${leagueId}`);
  }

  static async getStandings(leagueId: number): Promise<ApiResponse<Standing[]>> {
    return apiClient.get<ApiResponse<Standing[]>>(`/leagues/${leagueId}/standings`);
  }
}

export class TeamService {
  static async getTeamById(teamId: number): Promise<ApiResponse<Team>> {
    return apiClient.get<ApiResponse<Team>>(`/teams/${teamId}`);
  }

  static async searchTeams(query: string): Promise<ApiResponse<Team[]>> {
    return apiClient.get<ApiResponse<Team[]>>(`/teams/search?q=${query}`);
  }

  static async getTeamRecentMatches(
    teamId: number,
    limit: number = 5
  ): Promise<ApiResponse<any[]>> {
    return apiClient.get<ApiResponse<any[]>>(
      `/teams/${teamId}/recent-matches?limit=${limit}`
    );
  }
}

export class AuthService {
  static async login(email: string, password: string): Promise<ApiResponse<{
    token: string;
    userId: string;
    email: string;
  }>> {
    return apiClient.post<ApiResponse<{
      token: string;
      userId: string;
      email: string;
    }>>('/auth/login', { email, password });
  }

  static async register(
    email: string,
    password: string,
    name: string
  ): Promise<ApiResponse<{
    token: string;
    userId: string;
    email: string;
  }>> {
    return apiClient.post<ApiResponse<{
      token: string;
      userId: string;
      email: string;
    }>>('/auth/register', { email, password, name });
  }

  static async logout(): Promise<ApiResponse<void>> {
    return apiClient.post<ApiResponse<void>>('/auth/logout');
  }

  static async getMe(): Promise<ApiResponse<any>> {
    return apiClient.get<ApiResponse<any>>('/auth/me');
  }
}

export class UserService {
  static async uploadAvatar(formData: FormData): Promise<ApiResponse<{ avatarUrl: string }>> {
    return apiClient.post<ApiResponse<{ avatarUrl: string }>>('/users/me/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  static async addFavoriteTeam(teamId: number): Promise<ApiResponse<void>> {
    return apiClient.post<ApiResponse<void>>(`/users/me/favorites/teams/${teamId}`);
  }

  static async removeFavoriteTeam(teamId: number): Promise<ApiResponse<void>> {
    return apiClient.delete<ApiResponse<void>>(`/users/me/favorites/teams/${teamId}`);
  }
}
