import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from "@reduxjs/toolkit/query";

const baseQuery = fetchBaseQuery({
  baseUrl: "https://cafeapi.ru/api/v1",
  prepareHeaders: (headers, { endpoint }) => {
    const accessToken = localStorage.getItem("access_token");

    // ❌ Не добавлять access_token в login или refresh
    if (
      endpoint !== "logTelegram" &&
      endpoint !== "refreshToken" && // имя фиктивное, используем его позже
      accessToken
    ) {
      headers.set("Authorization", `Bearer ${accessToken}`);
    }

    return headers;
  },
});

export const baseQueryWithReauth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  let result = await baseQuery(args, api, extraOptions);

  if (result.error?.status === 401) {
    const refreshToken = localStorage.getItem("refresh_token");

    if (refreshToken) {
      
      const refreshResult = await baseQuery(
        {
          url: "/auth/telegram/refresh",
          method: "POST",
          headers: {
            "Authorization": `Bearer ${refreshToken}`, 
          },
        },
        { ...api, endpoint: "refreshToken" }, 
        extraOptions
      );

      if (refreshResult.data) {
        const newAccessToken = (refreshResult.data as any).access_token;
        localStorage.setItem("access_token", newAccessToken);

        // повторяем исходный запрос
        result = await baseQuery(args, api, extraOptions);
      } else {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        api.dispatch({ type: "auth/logout" });
      }
    }
  }

  return result;
};
