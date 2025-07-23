// src/app/store.ts
import { configureStore } from "@reduxjs/toolkit";
import { authApi } from "../features/auth/authApi";
import  authReducer  from "../features/auth/authSlice";
import { messageApi } from "../features/messanger/MessageApi";
import { telegramAuthApi } from "../features/auth/telegramAuthApi";
import modulSlice from '../features/moduls/modulsSlise'


export const store = configureStore({
  reducer: {
    [authApi.reducerPath]: authApi.reducer,
    [messageApi.reducerPath]: messageApi.reducer,
    [telegramAuthApi.reducerPath]: telegramAuthApi.reducer,
    auth: authReducer,
    modul:modulSlice
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(authApi.middleware, messageApi.middleware, telegramAuthApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
