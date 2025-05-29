import {createApi, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import {createBaseUrl} from '@root/util/api';

export const BASE_URL = '/level_sensor';

export interface LevelSensorData {
  x: number;
  y: number;
}

const levelsensorApi = createApi({
  baseQuery: fetchBaseQuery({
    baseUrl: createBaseUrl(BASE_URL),
  }),
  endpoints: (build) => ({
    getLevelSensorData: build.query<LevelSensorData, void>({
      query: () => ({url: `/data`}),
    }),
  }),
});

export default levelsensorApi;

export const {useGetLevelSensorDataQuery} = levelsensorApi;
