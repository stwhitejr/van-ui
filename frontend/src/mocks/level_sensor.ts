import {http, HttpResponse} from 'msw';
import {BASE_URL, LevelSensorData} from '@root/features/level_sensor/api';

export const mockData: LevelSensorData = {
  x: 1,
  y: 1,
};

export const handlers = [
  http.get(`${BASE_URL}/data`, async () => {
    return HttpResponse.json(mockData);
  }),
];
