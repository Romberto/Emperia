// features/sos/sosApi.ts
import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQueryWithReauth } from "../../app/baseQueryWithReauth";
import type { SosType } from "../../components/UI/Content/types";

export const messageApi = createApi({
  reducerPath: "messageApi",
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    sendSos: builder.mutation< 
      { status: string },
      { type: SosType; latitude: number; longitude: number }>({
      query: (body) => ({
        url: "send/sos",
        method: "POST",
        body,
      }),
    }),
  }),
});

export const { useSendSosMutation } = messageApi;
