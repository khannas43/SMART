import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Application {
  id: string;
  applicationNumber: string;
  schemeId: string;
  schemeName: string;
  status: string;
  submittedAt: string;
  updatedAt: string;
}

interface ApplicationState {
  applications: Application[];
  selectedApplication: Application | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: ApplicationState = {
  applications: [],
  selectedApplication: null,
  isLoading: false,
  error: null,
};

const applicationSlice = createSlice({
  name: 'application',
  initialState,
  reducers: {
    fetchApplicationsStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    fetchApplicationsSuccess: (state, action: PayloadAction<Application[]>) => {
      state.isLoading = false;
      state.applications = action.payload;
      state.error = null;
    },
    fetchApplicationsFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    selectApplication: (state, action: PayloadAction<Application>) => {
      state.selectedApplication = action.payload;
    },
    updateApplicationStatus: (state, action: PayloadAction<{ id: string; status: string }>) => {
      const index = state.applications.findIndex((app) => app.id === action.payload.id);
      if (index !== -1) {
        state.applications[index].status = action.payload.status;
        state.applications[index].updatedAt = new Date().toISOString();
      }
      if (state.selectedApplication?.id === action.payload.id) {
        state.selectedApplication.status = action.payload.status;
        state.selectedApplication.updatedAt = new Date().toISOString();
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  fetchApplicationsStart,
  fetchApplicationsSuccess,
  fetchApplicationsFailure,
  selectApplication,
  updateApplicationStatus,
  clearError,
} = applicationSlice.actions;
export default applicationSlice.reducer;

