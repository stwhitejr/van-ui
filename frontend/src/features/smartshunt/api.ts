import {createApi, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import {createBaseUrl} from '@root/util/api';

export const BASE_URL = '/smartshunt';

export interface SmartShuntData {
  voltage: string;
  current: string;
  power: string;
  state_of_charge_percent: string;
  consumed_ah: string;
  time_to_go_min: string;
}

const smartshuntApi = createApi({
  reducerPath: 'smartshunt',
  baseQuery: fetchBaseQuery({
    baseUrl: createBaseUrl(BASE_URL),
  }),
  endpoints: (build) => ({
    getSmartShuntData: build.query<SmartShuntData, void>({
      query: () => ({url: `/data`}),
    }),
  }),
});

export default smartshuntApi;

export const {useGetSmartShuntDataQuery} = smartshuntApi;
