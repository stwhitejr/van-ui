import {configureStore} from '@reduxjs/toolkit';
import {toastSlice} from '@root/features/toast/slice';
import inverterApi from '@root/features/inverter/api';
import smartshuntApi from '@root/features/smartshunt/api';
import levelsensorApi from '@root/features/level_sensor/api';
import {setupListeners} from '@reduxjs/toolkit/query';

export const createStore = (preloadedState?: Record<string, unknown>) => {
  const defaultConfig = {
    reducer: {
      [toastSlice.name]: toastSlice.reducer,
      [inverterApi.reducerPath]: inverterApi.reducer,
      [smartshuntApi.reducerPath]: smartshuntApi.reducer,
      [levelsensorApi.reducerPath]: levelsensorApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat([
        inverterApi.middleware,
        smartshuntApi.middleware,
        levelsensorApi.middleware,
      ]),
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
