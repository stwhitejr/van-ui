import {useToggleInverterMutation} from './api';
import {Box, Button} from '@mui/material';
import {useEffect} from 'react';
import useToast from '@root/features/toast/useToast';

const ToggleInverter = () => {
  const [toggle, response] = useToggleInverterMutation();
  const setToast = useToast();

  useEffect(() => {
    if (response.data) {
      setToast({
        message:
          response.data.error || response.data.on
            ? 'Inverter is on'
            : 'Inverter is off',
        status: response.data.success ? 'success' : 'error',
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
