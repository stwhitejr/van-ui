import {http, HttpResponse} from 'msw';
import {BASE_URL, ToggleResponse} from '@root/features/inverter/api';

export const mockData: ToggleResponse = {
  success: true,
};

export const handlers = [
  http.post(`${BASE_URL}/toggle`, async () => {
    return HttpResponse.json(mockData);
  }),
];
