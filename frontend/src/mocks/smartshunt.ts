import {http, HttpResponse} from 'msw';
import {BASE_URL, SmartShuntData} from '@root/features/smartshunt/api';

export const mockData: SmartShuntData = {
  voltage: 1,
  current: 1,
  power: 1,
  state_of_charge_percent: '80%',
  time_to_go_min: '8 Days remaining',
};

export const handlers = [
  http.get(`${BASE_URL}/data`, async () => {
    return HttpResponse.json(mockData);
  }),
];
