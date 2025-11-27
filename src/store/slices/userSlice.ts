import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { UserProfile, NotificationSettings } from '../../types';

interface UserState {
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: UserState = {
  profile: null,
  isLoading: false,
  error: null,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUserProfile: (state, action: PayloadAction<UserProfile>) => {
      state.profile = action.payload;
    },
    updateNotificationSettings: (state, action: PayloadAction<NotificationSettings>) => {
      if (state.profile) {
        state.profile.notificationSettings = action.payload;
      }
    },
    addFavoriteTeam: (state, action: PayloadAction<number>) => {
      if (state.profile && !state.profile.favoriteTeams.includes(action.payload)) {
        state.profile.favoriteTeams.push(action.payload);
      }
    },
    removeFavoriteTeam: (state, action: PayloadAction<number>) => {
      if (state.profile) {
        state.profile.favoriteTeams = state.profile.favoriteTeams.filter(
          (id) => id !== action.payload
        );
      }
    },
    addFavoriteLeague: (state, action: PayloadAction<number>) => {
      if (state.profile && !state.profile.favoriteLeagues.includes(action.payload)) {
        state.profile.favoriteLeagues.push(action.payload);
      }
    },
    removeFavoriteLeague: (state, action: PayloadAction<number>) => {
      if (state.profile) {
        state.profile.favoriteLeagues = state.profile.favoriteLeagues.filter(
          (id) => id !== action.payload
        );
      }
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
  setUserProfile,
  updateNotificationSettings,
  addFavoriteTeam,
  removeFavoriteTeam,
  addFavoriteLeague,
  removeFavoriteLeague,
  setLoading,
  setError,
} = userSlice.actions;
export default userSlice.reducer;
