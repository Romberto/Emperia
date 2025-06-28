import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { AuthResponse, TelegramAuthPayload } from "./types";

export const telegramAuthApi = createApi({
  reducerPath: "telegramAuthApi",
  baseQuery: fetchBaseQuery({
    baseUrl: "https://cafeapi.ru/api/v1",
    credentials: "include"
  }),
  endpoints: (builder) => ({
    logTelegram: builder.mutation<AuthResponse, TelegramAuthPayload>({
      query: (telegramPayload) => ({
        url: "/auth/telegram/login",
        method: "POST",
        body: telegramPayload,
      }),
    }),
  }),
});

export const { useLogTelegramMutation } = telegramAuthApi;