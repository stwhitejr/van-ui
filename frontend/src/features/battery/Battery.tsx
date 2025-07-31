import {Box, Stack} from '@mui/material';
import SmartShuntDashboard from '@root/features/smartshunt/SmartShuntDashboard';
import ToggleInverter from '@root/features/inverter/ToggleInverter';
import Container from '@root/components/Container';
import {useGetSmartShuntDataQuery} from '../smartshunt/api';
import RtkQueryGate from '@root/components/RtkQueryGate';
import {RefreshIcon} from '@root/components/icons';
import {useEffect, useState} from 'react';

const Battery = () => {
  const [data, setLocalCopy] = useState(null);
  const response = useGetSmartShuntDataQuery(undefined, {
    pollingInterval: 20000,
  });

  // Copy it to local state because often times the victron smartshunt doesn't always have the data
  // This prevent it from wiping it out and just falls back to the last good piece of data
  useEffect(() => {
    if (response.data?.voltage) {
      setLocalCopy(response.data);
    }
  }, [response.data]);
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
          {data && <SmartShuntDashboard data={data} />}
        </RtkQueryGate>
        <ToggleInverter />
      </Stack>
    </Container>
  );
};

export default Battery;
