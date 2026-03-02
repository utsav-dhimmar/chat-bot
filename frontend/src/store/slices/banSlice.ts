import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface BanState {
  isBanned: boolean;
  reason: string | null;
}

const initialState: BanState = {
  isBanned: false,
  reason: null,
};

const banSlice = createSlice({
  name: 'ban',
  initialState,
  reducers: {
    setBan(state, action: PayloadAction<string | null>) {
      state.isBanned = true;
      state.reason = action.payload;
    },
    clearBan(state) {
      state.isBanned = false;
      state.reason = null;
    },
  },
});

export const { setBan, clearBan } = banSlice.actions;
export default banSlice.reducer;
