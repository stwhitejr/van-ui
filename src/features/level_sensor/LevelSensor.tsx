import RtkQueryGate from '@root/components/RtkQueryGate';
import {useGetLevelSensorDataQuery} from './api';
import {Box} from '@mui/material';

const LevelSensor = () => {
  const response = useGetLevelSensorDataQuery();
  return (
    <Box border="solid 1px #ddd" p="10px">
      <h1>Van Level</h1>
      <RtkQueryGate {...response}>x: {response.data?.x}</RtkQueryGate>
    </Box>
  );
};

export default LevelSensor;
