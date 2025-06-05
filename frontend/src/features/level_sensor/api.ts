import {createApi, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import {createBaseUrl} from '@root/util/api';

export const BASE_URL = '/level_sensor';
export type LevelRating = 'Good' | 'Okay' | 'Bad';
export interface LevelSensorData {
  pitch: number;
  roll: number;
  level_percent: string;
  pitch_rating: LevelRating;
  roll_rating: LevelRating;
}

const levelsensorApi = createApi({
  reducerPath: 'levelsensor',
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
