import {configureStore} from '@reduxjs/toolkit';
import {toastSlice} from '@root/features/toast/slice';
import inverterApi from '@root/features/inverter/api';
import smartshuntApi from '@root/features/smartshunt/api';
import levelsensorApi from '@root/features/level_sensor/api';
import ledsApi from '@root/features/leds/api';
import filesApi from '@root/features/files/api';
import {setupListeners} from '@reduxjs/toolkit/query';
import appApi from './api';

export const createStore = (preloadedState?: Record<string, unknown>) => {
  const defaultConfig = {
    reducer: {
      [toastSlice.name]: toastSlice.reducer,
      [inverterApi.reducerPath]: inverterApi.reducer,
      [smartshuntApi.reducerPath]: smartshuntApi.reducer,
      [levelsensorApi.reducerPath]: levelsensorApi.reducer,
      [ledsApi.reducerPath]: ledsApi.reducer,
      [filesApi.reducerPath]: filesApi.reducer,
      [appApi.reducerPath]: appApi.reducer,
    },
    middleware: (getDefaultMiddleware) => [
      ...getDefaultMiddleware(),
      inverterApi.middleware,
      smartshuntApi.middleware,
      levelsensorApi.middleware,
      ledsApi.middleware,
      filesApi.middleware,
      appApi.middleware,
    ],
  };

  return preloadedState
    ? // @ts-ignore
      configureStore({
        ...defaultConfig,
        preloadedState,
      })
    : configureStore(defaultConfig);
};

export const store = createStore();

setupListeners(store.dispatch);

export type AppState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
