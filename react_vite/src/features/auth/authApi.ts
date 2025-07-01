// src/features/auth/authApi.ts
import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQueryWithReauth } from "../../app/baseQueryWithReauth";
import type { GetCurrentUser } from "./types";

export const authApi = createApi({
  reducerPath: "authApi",
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    // 👤 Получение текущего пользователя (по токену из localStorage)
    getCurrentUser: builder.query<GetCurrentUser, void>({
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
