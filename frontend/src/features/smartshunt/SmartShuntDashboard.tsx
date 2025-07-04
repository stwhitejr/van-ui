import RtkQueryGate from '@root/components/RtkQueryGate';
import {SmartShuntData, useGetSmartShuntDataQuery} from './api';
import {Box, Grid2, Stack} from '@mui/material';
import PillBox from '@root/components/PillBox';
import Text from '@root/components/Text';
import {ReactNode} from 'react';

const DataBox = ({children}: {children: ReactNode}) => {
  return (
    <PillBox
      gradiantDirection="180deg"
      sx={{
        textAlign: 'center',
        aspectRatio: 1 / 0.5,
        display: 'flex',
      }}
    >
      <Box margin="auto">{children}</Box>
    </PillBox>
  );
};

const SmartShuntDashboard = ({data}: {data: SmartShuntData}) => {
  return (
    <Stack spacing={2} alignItems="center">
      <PillBox
        gradiantDirection="180deg"
        sx={{
          flex: 2,
          borderRadius: '100%',
          textAlign: 'center',
          aspectRatio: 1 / 1,
          width: {
            xs: '50vw',
            sm: '50vw',
            md: '17vw',
          },
          display: 'flex',
        }}
      >
        <Box margin="auto">
          <Text size="title">{data.state_of_charge_percent}</Text>
          <Text size="small">{data.time_to_go_min}</Text>
        </Box>
      </PillBox>

      <Grid2 flex={1} container spacing={2} width="100%">
        <Grid2 size={4}>
          <DataBox>
            <Text size="body">{data.voltage}</Text>
            <Text size="small">voltage</Text>
          </DataBox>
        </Grid2>
        <Grid2 size={4}>
          <DataBox>
            <Text size="body">{data.current}</Text>
            <Text size="small">current</Text>
          </DataBox>
        </Grid2>
        <Grid2 size={4}>
          <DataBox>
            <Text size="body">{data.power}</Text>
            <Text size="small">power</Text>
          </DataBox>
        </Grid2>
      </Grid2>
    </Stack>
  );
};

export default SmartShuntDashboard;
