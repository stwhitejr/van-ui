import {createApi, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import {createBaseUrl} from '@root/util/api';

export const BASE_URL = '/inverter';

export interface ToggleResponse {
  success: boolean;
  on: boolean;
  error?: string;
}

const inverterApi = createApi({
  reducerPath: 'inverter',
  baseQuery: fetchBaseQuery({
    baseUrl: createBaseUrl(BASE_URL),
  }),
  endpoints: (build) => ({
    toggleInverter: build.mutation<ToggleResponse, void>({
      query: () => ({url: `/toggle`, method: 'post'}),
    }),
    getInverterStatus: build.query<{on: boolean}, void>({
      query: () => ({url: ``}),
    }),
  }),
});

export default inverterApi;

export const {useToggleInverterMutation, useGetInverterStatusQuery} =
  inverterApi;
