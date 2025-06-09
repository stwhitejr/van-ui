import {useToggleInverterMutation} from './api';
import {Box, Grid2} from '@mui/material';
import {useEffect} from 'react';
import useToast from '@root/features/toast/useToast';
import PillBox from '@root/components/PillBox';
import Text from '@root/components/Text';
import Button from '@root/components/Button';

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
    <Button onClick={toggle} sx={{height: '100%'}}>
      <Text size="large">Turn Inverter {response.data?.on ? 'Off' : 'On'}</Text>
    </Button>
  );
};

export default ToggleInverter;
