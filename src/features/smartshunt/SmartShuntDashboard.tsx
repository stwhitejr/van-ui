import RtkQueryGate from '@root/components/RtkQueryGate';
import {useGetSmartShuntDataQuery} from './api';
import {Box} from '@mui/material';

const SmartShuntDashboard = () => {
  const response = useGetSmartShuntDataQuery();
  return (
    <Box border="solid 1px #ddd" p="10px">
      <h1>Battery</h1>
      <RtkQueryGate {...response}>
        Voltage: {response.data?.voltage}
      </RtkQueryGate>
    </Box>
  );
};

export default SmartShuntDashboard;
