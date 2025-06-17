import {createApi, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import {createBaseUrl} from '@root/util/api';

export const BASE_URL = '/leds';

export type LEDPreset = 'rainbow' | 'pulse' | 'chase';

export interface LedResponse {
  on?: boolean;
  brightness?: number;
  color?: [number, number, number];
  preset?: LEDPreset | null;
  error?: string;
}

export interface LedConfigureRequest {
  on?: boolean;
  sleep?: number;
  brightness?: number;
  color?: string;
  preset?: LEDPreset;
}

const ledsApi = createApi({
  reducerPath: 'leds',
  baseQuery: fetchBaseQuery({
    baseUrl: createBaseUrl(BASE_URL),
  }),
  endpoints: (build) => ({
    ledsStatus: build.query<LedResponse, void>({
      query: () => ({url: ``}),
    }),
    configureLeds: build.mutation<LedResponse, LedConfigureRequest>({
      query: (body) => ({url: `/configure`, method: 'post', body}),
    }),
  }),
});

export default ledsApi;

export const {useConfigureLedsMutation, useLedsStatusQuery} = ledsApi;
