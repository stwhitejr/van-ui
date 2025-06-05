import {store} from '@root/store';
import {Provider} from 'react-redux';
import Toast from '@root/features/toast/Toast';
import {Box, Grid2, Stack} from '@mui/material';
import SmartShuntDashboard from '@root/features/smartshunt/SmartShuntDashboard';
import ToggleInverter from '@root/features/inverter/ToggleInverter';
import LevelSensor from '@root/features/level_sensor/LevelSensor';
import './App.css';

const App = () => {
  return (
    <Provider store={store}>
      <Box
        sx={{
          p: 1,
          display: 'flex',
          flexDirection: 'row',
        }}
      >
        <Grid2 flex={1} container spacing={2}>
          <Grid2 size={6}>
            <LevelSensor />
          </Grid2>
          <Grid2 size={6}>
            <Stack spacing={2}>
              <SmartShuntDashboard />
              <ToggleInverter />
            </Stack>
          </Grid2>
        </Grid2>
      </Box>
      <Toast />
    </Provider>
  );
};

export default App;
