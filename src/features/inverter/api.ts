import {createApi, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import {createBaseUrl} from '@root/util/api';

export const BASE_URL = '/inverter';

export interface ToggleResponse {
  success: boolean;
}

const inverterApi = createApi({
  baseQuery: fetchBaseQuery({
    baseUrl: createBaseUrl(BASE_URL),
  }),
  endpoints: (build) => ({
    toggleInverter: build.mutation<ToggleResponse, void>({
      query: () => ({url: `/toggle`}),
    }),
  }),
});

export default inverterApi;

export const {useToggleInverterMutation} = inverterApi;
