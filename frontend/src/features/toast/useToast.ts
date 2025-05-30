import {setToast, ToastState} from '@root/features/toast/slice';
import {useCallback} from 'react';
import {useDispatch} from 'react-redux';

const useToast = () => {
  const dispatch = useDispatch();
  return useCallback(
    (args: ToastState) => dispatch(setToast(args)),
    [dispatch]
  );
};

export default useToast;
