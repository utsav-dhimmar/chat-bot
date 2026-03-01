import type { UserProfile } from "@/apis/types/auth.types";
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

interface AuthState {
	user: UserProfile | null;
	token: string | null;
	isAuthenticated: boolean;
}

const initialState: AuthState = {
	user: JSON.parse(localStorage.getItem("user") || "null"),
	token: localStorage.getItem("token") || null,
	isAuthenticated: !!localStorage.getItem("token"),
};

const authSlice = createSlice({
	name: "auth",
	initialState,
	reducers: {
		setCredentials: (
			state,
			action: PayloadAction<{ user: UserProfile; token: string }>,
		) => {
			const { user, token } = action.payload;
			state.user = user;
			state.token = token;
			state.isAuthenticated = true;
			localStorage.setItem("token", token);
			localStorage.setItem("user", JSON.stringify(user));
		},
		logout: state => {
			state.user = null;
			state.token = null;
			state.isAuthenticated = false;
			localStorage.removeItem("token");
			localStorage.removeItem("user");
		},
		updateUser: (state, action: PayloadAction<UserProfile>) => {
			state.user = action.payload;
			localStorage.setItem("user", JSON.stringify(action.payload));
		},
	},
});

export const { setCredentials, logout, updateUser } = authSlice.actions;
export default authSlice.reducer;
