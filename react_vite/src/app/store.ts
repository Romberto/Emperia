// src/app/store.ts
import { configureStore } from "@reduxjs/toolkit";
import { authApi } from "../features/auth/authApi";
import  authReducer  from "../features/auth/authSlice";

export const store = configureStore({
  reducer: {
    [authApi.reducerPath]: authApi.reducer,
    auth: authReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(authApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
