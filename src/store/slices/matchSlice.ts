import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Match, MatchFilter } from '../../types';

interface MatchState {
  upcomingMatches: Match[];
  liveMatches: Match[];
  finishedMatches: Match[];
  followedMatches: number[];
  filters: MatchFilter;
  isLoading: boolean;
  error: string | null;
}

const initialState: MatchState = {
  upcomingMatches: [],
  liveMatches: [],
  finishedMatches: [],
  followedMatches: [],
  filters: {},
  isLoading: false,
  error: null,
};

const matchSlice = createSlice({
  name: 'matches',
  initialState,
  reducers: {
    setUpcomingMatches: (state, action: PayloadAction<Match[]>) => {
      state.upcomingMatches = action.payload;
    },
    setLiveMatches: (state, action: PayloadAction<Match[]>) => {
      state.liveMatches = action.payload;
    },
    setFinishedMatches: (state, action: PayloadAction<Match[]>) => {
      state.finishedMatches = action.payload;
    },
    toggleFollowMatch: (state, action: PayloadAction<number>) => {
      const matchId = action.payload;
      const index = state.followedMatches.indexOf(matchId);
      if (index > -1) {
        state.followedMatches.splice(index, 1);
      } else {
        state.followedMatches.push(matchId);
      }
    },
    setFilters: (state, action: PayloadAction<MatchFilter>) => {
      state.filters = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const {
  setUpcomingMatches,
  setLiveMatches,
  setFinishedMatches,
  toggleFollowMatch,
  setFilters,
  setLoading,
  setError,
} = matchSlice.actions;
export default matchSlice.reducer;
