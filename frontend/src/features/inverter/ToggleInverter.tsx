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
    <Grid2 container spacing={2} width="100%">
      <Grid2 size={4}>
        <PillBox
          gradiantDirection="180deg"
          gradiantVariation={response.data?.on ? 'on' : 'default'}
          sx={{
            textAlign: 'center',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Text size="body">{response.data?.on ? 'Inverting' : 'Off'}</Text>
        </PillBox>
      </Grid2>

      <Grid2 size={8}>
        <Button onClick={toggle}>
          <Text size="large">Toggle Inverter</Text>
        </Button>
      </Grid2>
    </Grid2>
  );
};

export default ToggleInverter;
