import {handlers as smartshuntHandlers} from './smartshunt';
import {handlers as levelsensorHandlers} from './level_sensor';
import {handlers as inverterHandlers} from './inverter';

export default [
  ...smartshuntHandlers,
  ...levelsensorHandlers,
  ...inverterHandlers,
];
