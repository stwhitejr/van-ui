import {useToggleInverterMutation} from './api';
import {Box, Button, Container} from '@mui/material';
import {useEffect} from 'react';
import useToast from '@root/features/toast/useToast';

const ToggleInverter = () => {
  const [toggle, response] = useToggleInverterMutation();
  const setToast = useToast();

  useEffect(() => {
    if (response.data) {
      setToast({
        message: response.data ? 'success' : 'failure',
        status: response.data ? 'success' : 'error',
      });
    }
  }, [response, setToast]);

  return (
    <Box border="solid 1px #ddd" p="10px">
      <h1>Inverter</h1>
      <Button onClick={() => toggle()}>Toggle</Button>
    </Box>
  );
};

export default ToggleInverter;
