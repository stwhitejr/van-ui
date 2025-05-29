import {createApi, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import {Snowboard, Snowboards} from './types';
import {createBaseUrl} from '@root/util/api';

export const BASE_URL = '/v1/winter';

export type SnowboardQuery = Partial<Snowboard>;

const api = createApi({
  baseQuery: fetchBaseQuery({
    baseUrl: createBaseUrl(BASE_URL),
  }),
  endpoints: (build) => ({
    getSnowboards: build.query<Snowboards, SnowboardQuery | void>({
      query: () => ({url: `/snowboards`}),
    }),
  }),
});

export default api;

export const {useGetSnowboardsQuery} = api;
