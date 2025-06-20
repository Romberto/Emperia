// src/features/auth/authSlice.ts
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

interface AuthState {
  username?: string;
}

const initialState: AuthState = {
  username: undefined,
};

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<{ username?: string }>) => {
      state.username = action.payload.username;
    },
  },
});

export const { setUser } = authSlice.actions;
export default authSlice.reducer;
