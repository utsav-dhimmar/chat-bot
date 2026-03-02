import { ChatServices } from '@/apis/services/chat.service';
import type { ChatSession } from '@/apis/types/chat.types';
import { createAsyncThunk, createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface ChatState {
  sessions: ChatSession[];
  loading: boolean;
  error: string | null;
}

const initialState: ChatState = {
  sessions: [],
  loading: false,
  error: null,
};

export const fetchSessions = createAsyncThunk('chat/fetchSessions', async () => {
  const sessions = await ChatServices.listSessions();
  return sessions;
});

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setSessions: (state, action: PayloadAction<ChatSession[]>) => {
      state.sessions = action.payload;
    },
    clearSessions: (state) => {
      state.sessions = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSessions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSessions.fulfilled, (state, action) => {
        state.loading = false;
        state.sessions = action.payload;
      })
      .addCase(fetchSessions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch sessions';
      });
  },
});

export const { setSessions, clearSessions } = chatSlice.actions;
export default chatSlice.reducer;
