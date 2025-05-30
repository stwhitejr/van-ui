import {useSelector} from 'react-redux';
import {selectToast} from './selectors';
import {Alert, Snackbar} from '@mui/material';
import useToast from './useToast';
import {useEffect} from 'react';

const Toast = () => {
  const state = useSelector(selectToast);
  const setToast = useToast();

  useEffect(() => {
    if (state.message) {
      setTimeout(() => {
        setToast({message: null, status: null});
      }, 5000);
    }
  }, [state, setToast]);

  if (state.message) {
    return (
      <Snackbar open>
        <Alert severity={state.status}>{state.message}</Alert>
      </Snackbar>
    );
  }
  return null;
};

export default Toast;
