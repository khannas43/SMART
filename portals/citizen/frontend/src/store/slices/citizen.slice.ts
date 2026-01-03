import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface CitizenProfile {
  id: string;
  name: string;
  dateOfBirth?: string;
  gender?: string;
  mobile: string;
  email?: string;
  address?: string;
  district?: string;
  pincode?: string;
  verificationStatus?: string;
}

interface CitizenState {
  profile: CitizenProfile | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: CitizenState = {
  profile: null,
  isLoading: false,
  error: null,
};

const citizenSlice = createSlice({
  name: 'citizen',
  initialState,
  reducers: {
    fetchProfileStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    fetchProfileSuccess: (state, action: PayloadAction<CitizenProfile>) => {
      state.isLoading = false;
      state.profile = action.payload;
      state.error = null;
    },
    fetchProfileFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    updateProfile: (state, action: PayloadAction<Partial<CitizenProfile>>) => {
      if (state.profile) {
        state.profile = { ...state.profile, ...action.payload };
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const { fetchProfileStart, fetchProfileSuccess, fetchProfileFailure, updateProfile, clearError } =
  citizenSlice.actions;
export default citizenSlice.reducer;

