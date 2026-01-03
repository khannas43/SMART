import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/auth.slice';
import citizenReducer from './slices/citizen.slice';
import applicationReducer from './slices/application.slice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    citizen: citizenReducer,
    application: applicationReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

