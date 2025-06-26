// src/shared/api/baseQueryWithReauth.ts
import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from "@reduxjs/toolkit/query";

const baseQuery = fetchBaseQuery({
  baseUrl: "https://cafeapi.ru/api/v1",
  prepareHeaders: (headers) => {
    const token = localStorage.getItem("access_token");
    if (token) headers.set("Authorization", `Bearer ${token}`);
    return headers;
  },
});

export const baseQueryWithReauth: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> =
  async (args, api, extraOptions) => {
    let result = await baseQuery(args, api, extraOptions);

    // если access токен протух
    if (result.error?.status === 401) {
      const refresh_token = localStorage.getItem("refresh_token");

      if (refresh_token) {
        // запрос на refresh
        const refreshResult = await baseQuery(
          {
            url: "/auth/refresh",
            method: "POST",
            body: { refresh_token },
          },
          api,
          extraOptions
        );

        if (refreshResult.data) {
          const newAccessToken = (refreshResult.data as any).access_token;
          localStorage.setItem("access_token", newAccessToken);

          // Повторяем оригинальный запрос
          result = await baseQuery(args, api, extraOptions);
        } else {
          // refresh тоже не сработал — логаут
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          api.dispatch({ type: "auth/logout" }); // нужно добавить в slice
        }
      }
    }

    return result;
  };
