import {Box, Grid2, Stack} from '@mui/material';
import SmartShuntDashboard from '@root/features/smartshunt/SmartShuntDashboard';
import ToggleInverter from '@root/features/inverter/ToggleInverter';
import LevelSensor from '@root/features/level_sensor/LevelSensor';
import './App.css';
import {useState} from 'react';
import LedController from './features/leds/LedController';
import Button from './components/Button';
import Text from './components/Text';

const Pages = () => {
  const [pageNumber, setPageNumber] = useState(2);
  return (
    <Box
      sx={{
        display: 'flex',
        minHeight: '100vh',
      }}
    >
      {pageNumber === 1 && (
        <Grid2 container alignItems="center">
          <Grid2 size={12} textAlign="center">
            <Box display="inline-block">
              <Button onClick={() => setPageNumber(2)}>
                <Text size="body">Configure LEDs</Text>
              </Button>
            </Box>
          </Grid2>
          <Grid2 size={6} p={2}>
            <LevelSensor />
          </Grid2>
          <Grid2 size={6} p={2}>
            <Stack spacing={2}>
              <SmartShuntDashboard />
              <ToggleInverter />
            </Stack>
          </Grid2>
        </Grid2>
      )}
      {pageNumber === 2 && (
        <Grid2 container alignSelf="center" alignItems="center" width="100%">
          <Grid2 size={12} textAlign="center">
            <Box display="inline-block">
              <Button onClick={() => setPageNumber(1)}>
                <Text size="body">Back</Text>
              </Button>
            </Box>
          </Grid2>
          <Grid2 size={12}>
            <LedController />
          </Grid2>
        </Grid2>
      )}
    </Box>
  );
};

export default Pages;
