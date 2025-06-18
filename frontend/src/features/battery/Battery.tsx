import {Box, Stack} from '@mui/material';
import SmartShuntDashboard from '@root/features/smartshunt/SmartShuntDashboard';
import ToggleInverter from '@root/features/inverter/ToggleInverter';
import Container from '@root/components/Container';
import {useGetSmartShuntDataQuery} from '../smartshunt/api';
import RtkQueryGate from '@root/components/RtkQueryGate';
import {RefreshIcon} from '@root/components/icons';

const Battery = () => {
  const response = useGetSmartShuntDataQuery(undefined, {
    pollingInterval: 20000,
  });
  return (
    <Container
      title="Battery Monitor"
      additional={
        <Box sx={{cursor: 'pointer'}} onClick={() => response.refetch()}>
          <RefreshIcon />
        </Box>
      }
    >
      <Stack spacing={2}>
        <RtkQueryGate {...response}>
          {response.data && <SmartShuntDashboard data={response.data} />}
        </RtkQueryGate>
        <ToggleInverter />
      </Stack>
    </Container>
  );
};

export default Battery;
