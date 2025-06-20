// src/features/auth/authSlice.ts
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

interface AuthState {
  username?: string;
  first_name?: string;
  photo_url?: string;
}

const initialState: AuthState = {
  username: "Romberto",
  first_name: undefined,
  photo_url: undefined,
};

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setUser: (
      state,
      action: PayloadAction<{
        username?: string;
        first_name?: string;
        photo_url?: string;
      }>
    ) => {
      state.username = action.payload.username;
      state.first_name = action.payload.first_name;
      state.photo_url = action.payload.photo_url;
    },
  },
});

export const { setUser } = authSlice.actions;
export default authSlice.reducer;
