// src/features/auth/authSlice.ts
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
interface AuthState {
  username?: string;
  first_name?: string;
  photo_url?: string;
  access_token?: string;
  refresh_token?: string;
}

 const loadFromLocalStorage =  (): AuthState => {

  try {
    return {
      username: localStorage.getItem("username") ?? undefined,
      first_name: localStorage.getItem("tg_first_name") ?? undefined,
      photo_url: localStorage.getItem("tg_photo_url") ?? undefined,
      access_token: localStorage.getItem("access_token") ?? undefined,
      refresh_token: localStorage.getItem("refresh_token") ?? undefined};
      
  } catch (e) {
    return {};
  }
};

const initialState: AuthState = loadFromLocalStorage();



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
        access_token?: string;
        refresh_token?: string;
      }>
    ) => {
      Object.assign(state, action.payload);
    },
    logout: (state) => {
      state.username = undefined;
      state.first_name = undefined;
      state.photo_url = undefined;
      state.access_token = undefined;
      state.refresh_token = undefined;
    },
  },
});

export const { setUser, logout } = authSlice.actions;
export default authSlice.reducer;
