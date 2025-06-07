import {createApi, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import {createBaseUrl} from '@root/util/api';

export const BASE_URL = '/leds';

export interface LedConfigureResponse {
  success: boolean;
  on: boolean;
  error?: string;
}

export interface LedConfigureRequest {
  on?: boolean;
  sleep?: number;
  brightness?: number;
  color?: string;
  preset?: 'rainbow' | 'pulse' | 'chase';
}

const ledsApi = createApi({
  reducerPath: 'leds',
  baseQuery: fetchBaseQuery({
    baseUrl: createBaseUrl(BASE_URL),
  }),
  endpoints: (build) => ({
    configureLeds: build.mutation<LedConfigureResponse, LedConfigureRequest>({
      query: (body) => ({url: `/configure`, method: 'post', body}),
    }),
  }),
});

export default ledsApi;

export const {useConfigureLedsMutation} = ledsApi;
