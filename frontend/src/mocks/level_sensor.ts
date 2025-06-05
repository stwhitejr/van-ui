import {http, HttpResponse} from 'msw';
import {BASE_URL, LevelSensorData} from '@root/features/level_sensor/api';

export const mockData: LevelSensorData = {
  pitch: 1,
  roll: -3,
  level_percent: '90%',
  pitch_rating: 'Good',
  roll_rating: 'Okay',
};

export const handlers = [
  http.get(`${BASE_URL}/data`, async () => {
    return HttpResponse.json(mockData);
  }),
];
