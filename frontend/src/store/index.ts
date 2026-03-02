import { configureStore } from '@reduxjs/toolkit';
import adminReducer from './slices/adminSlice';
import authReducer from './slices/authSlice';
import banReducer from './slices/banSlice';
import chatReducer from './slices/chatSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    admin: adminReducer,
    ban: banReducer,
    chat: chatReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
