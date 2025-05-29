import {SnowboardTypes} from './constants';

export type SnowboardType = typeof SnowboardTypes;

export interface Snowboard {
  id: number;
  brand: string;
  model: string;
  length: number;
  type: SnowboardType[number];
}

export type Snowboards = Snowboard[];
