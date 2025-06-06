import {handlers as smartshuntHandlers} from './smartshunt';
import {handlers as levelsensorHandlers} from './level_sensor';
import {handlers as inverterHandlers} from './inverter';
import {handlers as ledsHandler} from './leds';

export default [
  ...smartshuntHandlers,
  ...levelsensorHandlers,
  ...inverterHandlers,
  ...ledsHandler,
];
