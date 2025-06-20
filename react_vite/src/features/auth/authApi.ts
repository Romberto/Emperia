// src/features/auth/authApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

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
  reducerPath: 'authApi',
  baseQuery: fetchBaseQuery({
    baseUrl: 'https://cafeapi.ru/api/v1',
  }),
  endpoints: (builder) => ({
    // 🔁 Telegram login — теперь принимает весь payload
    loginTelegram: builder.mutation<AuthResponse, TelegramAuthPayload>({
      query: (telegramPayload) => ({
        url: '/auth/telegram/login',
        method: 'POST',
        body: telegramPayload,
      }),
    }),
    // 👤 Получение текущего пользователя (по токену из localStorage)
    getCurrentUser: builder.query<any, void>({
      query: () => ({
        url: '/user/me',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      }),
    }),
  }),
});

export const {
  useLoginTelegramMutation,
  useGetCurrentUserQuery,
} = authApi;
