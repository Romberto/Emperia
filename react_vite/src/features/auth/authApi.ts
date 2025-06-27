// src/features/auth/authApi.ts
import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQueryWithReauth } from "../../app/baseQueryWithReauth";

export interface TelegramAuthPayload {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  
}

export const authApi = createApi({
  reducerPath: "authApi",
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    // 👤 Получение текущего пользователя (по токену из localStorage)
    getCurrentUser: builder.query<any, void>({
      query: () => ({
        url: "/user/me",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      }),
    }),
    refreshToken: builder.mutation<{ access_token: string }, { refresh_token: string }>({
      query: (data) => ({
        url: "/auth/refresh",
        method: "POST",
        body: data,
      }),
    }),
  }),
});

export const { useGetCurrentUserQuery, useRefreshTokenMutation } = authApi;
