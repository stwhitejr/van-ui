import {http, HttpResponse} from 'msw';
import {BASE_URL, LedConfigureResponse} from '@root/features/leds/api';

export const mockData: LedConfigureResponse = {
  success: true,
};

export const handlers = [
  http.post(`${BASE_URL}/configure`, async () => {
    return HttpResponse.json(mockData);
  }),
];
