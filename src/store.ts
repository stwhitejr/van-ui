import {configureStore} from '@reduxjs/toolkit';
import {toastSlice} from '@root/features/toast/slice';
import snowboardsApi from '@root/features/snowboards/api';
import {setupListeners} from '@reduxjs/toolkit/query';

export const createStore = (preloadedState?: Record<string, unknown>) => {
  const defaultConfig = {
    reducer: {
      [toastSlice.name]: toastSlice.reducer,
      [snowboardsApi.reducerPath]: snowboardsApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(snowboardsApi.middleware),
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
