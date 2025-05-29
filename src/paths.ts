import {path} from 'static-path';

export const snowboardsPath = path('/');
export const snowboardPath = snowboardsPath.path('/:id');
