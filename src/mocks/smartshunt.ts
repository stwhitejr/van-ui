import {http, HttpResponse} from 'msw';
import {BASE_URL, SmartShuntData} from '@root/features/smartshunt/api';

export const mockData: SmartShuntData = {
  voltage: 1,
};

export const handlers = [
  http.get(`${BASE_URL}/data`, async () => {
    return HttpResponse.json(mockData);
  }),
];
