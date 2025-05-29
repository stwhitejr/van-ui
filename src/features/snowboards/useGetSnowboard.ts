import {useSelector} from 'react-redux';
import api from './api';
import {createSelector} from '@reduxjs/toolkit';
import {AppState} from '@root/store';

const selectSnowboardList = api.endpoints.getSnowboards.select();

const selectSnowboardFromList = createSelector(
  selectSnowboardList,
  (state: AppState, id: number | string) => id,
  (listResponse, _id) => {
    if (!listResponse.data) {
      return null;
    }
    const id = typeof _id === 'string' ? parseInt(_id, 10) : _id;
    const match = listResponse.data.find((snowboard) => snowboard.id === id);
    return match || null;
  }
);

// Reuse list cache if we have it otherwise use get snowboard API
const useGetSnowboard = (id: string | number) => {
  const snowboardFromListCache = useSelector((state: AppState) =>
    selectSnowboardFromList(state, id)
  );
  // This is where you would call an individual get snowboard API if you don't have it in the list already something like this
  // const {} = useGetSnowboard(id, {skip: !!snowboardFromListCache})

  return snowboardFromListCache;
};

export default useGetSnowboard;
