import {createApi, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import {createBaseUrl} from '@root/util/api';

export const BASE_URL = '/app';

const appApi = createApi({
  reducerPath: 'app',
  baseQuery: fetchBaseQuery({
    baseUrl: createBaseUrl(BASE_URL),
  }),
  endpoints: (build) => ({
    killApp: build.mutation<void, void>({
      query: () => ({url: `/kill`}),
    }),
  }),
});

export default appApi;

export const {useKillAppMutation} = appApi;
