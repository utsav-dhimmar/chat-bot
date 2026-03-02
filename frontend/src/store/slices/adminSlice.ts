import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface AdminState {
  token: string | null;
  email: string | null;
  isAuthenticated: boolean;
}

const initialState: AdminState = {
  token: localStorage.getItem('adminToken') || null,
  email: localStorage.getItem('adminEmail') || null,
  isAuthenticated: !!localStorage.getItem('adminToken'),
};

const adminSlice = createSlice({
  name: 'admin',
  initialState,
  reducers: {
    setAdminCredentials: (state, action: PayloadAction<{ token: string; email: string }>) => {
      const { token, email } = action.payload;
      state.token = token;
      state.email = email;
      state.isAuthenticated = true;
      localStorage.setItem('adminToken', token);
      localStorage.setItem('adminEmail', email);
    },
    logoutAdmin: (state) => {
      state.token = null;
      state.email = null;
      state.isAuthenticated = false;
      localStorage.removeItem('adminToken');
      localStorage.removeItem('adminEmail');
    },
  },
});

export const { setAdminCredentials, logoutAdmin } = adminSlice.actions;
export default adminSlice.reducer;
