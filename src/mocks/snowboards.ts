import {http, HttpResponse} from 'msw';
import {BASE_URL} from '@root/features/snowboards/api';
import {Snowboard} from '@root/features/snowboards/types';

export const snowboardMock: Snowboard = {
  id: 1,
  brand: 'Never Summer',
  length: 158,
  type: 'Powder',
  model: 'Harpoon',
};

export const snowboardsMock: Snowboard[] = [
  snowboardMock,
  {
    id: 2,
    brand: 'Never Summer',
    length: 154,
    type: 'Freestyle',
    model: 'Protoslinger',
  },
  {
    id: 3,
    brand: 'Yes',
    length: 156,
    type: 'Freestyle',
    model: 'Greats',
  },
  {
    id: 4,
    brand: 'Libtech',
    length: 160,
    type: 'Freeride',
    model: 'Orca',
  },
];

export const handlers = [
  http.get(`${BASE_URL}/snowboards`, async () => {
    return HttpResponse.json(snowboardsMock);
  }),
];
