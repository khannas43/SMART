import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { authService, citizenService } from '@/services';
import { User } from '@/types/api';

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  profileNotFound: boolean; // Flag to indicate profile needs to be created
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('auth_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  isAuthenticated: !!localStorage.getItem('auth_token'),
  isLoading: false,
  error: null,
  profileNotFound: false,
};

// Async thunk for login using test token endpoint (backward compatibility)
export const loginWithTestToken = createAsyncThunk(
  'auth/loginWithTestToken',
  async (username: string = 'test-user', { rejectWithValue }) => {
    try {
      // Get test token
      const tokenResponse = await authService.getTestToken(username);
      const token = tokenResponse.token;

      // Store token
      localStorage.setItem('auth_token', token);
      localStorage.setItem('refresh_token', token); // Using same token for refresh for now

      // Try to get current user profile (if endpoint exists)
      let user: User | null = null;
      let profileNotFound = false;
      try {
        // Try to fetch actual user profile
        user = await citizenService.getCurrentUser();
      } catch (error: any) {
        // If profile fetch fails (404 = profile not found, or other error)
        // Don't create a mock user - user will be null and components should handle it
        if (error.response?.status === 404) {
          profileNotFound = true;
          console.log('User profile not found - profile needs to be created');
        } else {
          console.log('Error fetching user profile:', error.response?.status, error.response?.data?.message);
        }
        // Return null user - components should handle this gracefully
        // The token is still valid, but user profile needs to be created
        // This is expected for new users who haven't completed their profile yet
      }
      
      // Return success with token (user may be null if profile doesn't exist yet)
      // Components should check for user existence before making API calls
      return { 
        user: user || null, // Explicitly set to null if not found
        token, 
        refreshToken: token,
        profileNotFound
      };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Login failed');
    }
  }
);

// Async thunk for login with OTP verification
export const loginWithOTP = createAsyncThunk(
  'auth/loginWithOTP',
  async (params: { janAadhaarId: string; otp: string }, { rejectWithValue }) => {
    try {
      // Verify OTP and get token
      const tokenResponse = await authService.verifyOTP(params.janAadhaarId, params.otp);
      const token = tokenResponse.token;

      // Store token
      localStorage.setItem('auth_token', token);
      localStorage.setItem('refresh_token', token);

      // Try to get current user profile
      let user: User | null = null;
      let profileNotFound = false;
      try {
        user = await citizenService.getCurrentUser();
      } catch (error: any) {
        if (error.response?.status === 404) {
          profileNotFound = true;
          console.log('User profile not found - profile needs to be created');
        } else {
          console.log('Error fetching user profile:', error.response?.status, error.response?.data?.message);
        }
      }
      
      return { 
        user: user || null,
        token, 
        refreshToken: token,
        profileNotFound
      };
    } catch (error: any) {
      console.error('OTP verification error:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.error || 
                          error.message || 
                          'OTP verification failed. Please check your OTP (use 123456 for testing).';
      return rejectWithValue(errorMessage);
    }
  }
);

// Async thunk for fetching current user profile
export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const user = await citizenService.getCurrentUser();
      return user;
    } catch (error: any) {
      // If 404 (user not found), don't treat it as a critical error
      // The dashboard can still work without user profile
      if (error.response?.status === 404) {
        return rejectWithValue('USER_NOT_FOUND');
      }
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch user profile');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    loginSuccess: (state, action: PayloadAction<{ user: User; token: string; refreshToken: string }>) => {
      state.isLoading = false;
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.refreshToken = action.payload.refreshToken;
      state.error = null;
    },
    loginFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.isAuthenticated = false;
      state.error = action.payload;
    },
    logout: (state) => {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.error = null;
      state.profileNotFound = false;
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    clearError: (state) => {
      state.error = null;
    },
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
      localStorage.setItem('auth_token', action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      // Login with test token
      .addCase(loginWithTestToken.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginWithTestToken.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        // Only set user if it's not null (profile was found)
        // If user is null, token is still valid but profile needs to be created
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.profileNotFound = action.payload.profileNotFound || false;
        state.error = null;
      })
      .addCase(loginWithTestToken.rejected, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      })
      // Login with OTP
      .addCase(loginWithOTP.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginWithOTP.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.profileNotFound = action.payload.profileNotFound || false;
        state.error = null;
      })
      .addCase(loginWithOTP.rejected, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      })
      // Fetch current user
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload;
        state.profileNotFound = false;
      })
      .addCase(fetchCurrentUser.rejected, (state, action) => {
        // Don't clear auth state on profile fetch failure
        // If 404, mark that profile needs to be created
        if (action.payload === 'USER_NOT_FOUND') {
          state.profileNotFound = true;
          state.user = null; // Clear any existing user data
        }
        state.error = action.payload as string;
      });
  },
});

export const { loginStart, loginSuccess, loginFailure, logout, updateUser, clearError, setToken } =
  authSlice.actions;
export default authSlice.reducer;

