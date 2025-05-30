import {createSlice} from '@reduxjs/toolkit';
import type {PayloadAction} from '@reduxjs/toolkit';

export interface ToastState {
  message: string | null;
  status: 'success' | 'error' | 'warning' | 'info';
}

const initialState: ToastState = {
  message: null,
  status: null,
};

// This redux is completely pointless in this dummy application but th
export const toastSlice = createSlice({
  name: 'toast',
  initialState,
  reducers: {
    setToast: (state, action: PayloadAction<ToastState>) => {
      return action.payload;
    },
  },
});

export const {setToast} = toastSlice.actions;

export default toastSlice.reducer;
