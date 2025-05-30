import {store} from '@root/store';
import {Provider} from 'react-redux';
import Toast from '@root/features/toast/Toast';
import {Stack} from '@mui/material';
import SmartShuntDashboard from '@root/features/smartshunt/SmartShuntDashboard';
import ToggleInverter from '@root/features/inverter/ToggleInverter';
import LevelSensor from '@root/features/level_sensor/LevelSensor';

const App = () => {
  return (
    <Provider store={store}>
      <Stack spacing="10px">
        <SmartShuntDashboard />
        <ToggleInverter />
        <LevelSensor />
      </Stack>

      <Toast />
    </Provider>
  );
};

export default App;
