import {useGetInverterStatusQuery, useToggleInverterMutation} from './api';
import {useEffect} from 'react';
import useToast from '@root/features/toast/useToast';
import Text from '@root/components/Text';
import Button from '@root/components/Button';
import RtkQueryGate from '@root/components/RtkQueryGate';

const ToggleInverter = () => {
  const inverterStatusResponse = useGetInverterStatusQuery(undefined, {
    refetchOnMountOrArgChange: true,
  });
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

  const isOn = response.data
    ? response.data?.on
    : inverterStatusResponse.data?.on;

  return (
    <RtkQueryGate {...inverterStatusResponse}>
      <Button onClick={toggle} sx={{height: '100%'}}>
        <Text size="large">Turn Inverter {isOn ? 'Off' : 'On'}</Text>
      </Button>
    </RtkQueryGate>
  );
};

export default ToggleInverter;
