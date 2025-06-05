import RtkQueryGate from '@root/components/RtkQueryGate';
import {LevelRating, useGetLevelSensorDataQuery} from './api';
import {Box, Stack} from '@mui/material';
import Text from '@root/components/Text';
import PillBox from '@root/components/PillBox';
import {ReactNode} from 'react';
import van_front from '@root/assets/images/van_front.png';
import van_side from '@root/assets/images/van_side.png';

const backgroundByRating = {
  Good: 'linear-gradient(0deg, #2ca650 0%,rgb(103, 216, 137) 100%)',
  Okay: 'linear-gradient(0deg, #c0972e 0%,rgb(234, 197, 104) 100%)',
  Bad: 'linear-gradient(0deg, #9a3434 0%,rgb(203, 96, 96) 100%)',
};

const LevelData = ({
  image,
  children,
  rating,
}: {
  image: ReactNode;
  children: ReactNode;
  rating: LevelRating;
}) => {
  return (
    <Stack spacing={2} useFlexGap alignItems="center" width="50%">
      <Box width="90%" textAlign="center">
        {image}
      </Box>
      <PillBox
        sx={{
          width: '100%',
          display: 'flex',
          background: backgroundByRating[rating],
        }}
      >
        <Stack
          flexDirection="row"
          justifyContent="space-between"
          spacing={2}
          useFlexGap
          alignItems="center"
          margin="auto"
        >
          {children}
        </Stack>
      </PillBox>
    </Stack>
  );
};

const LevelSensor = () => {
  const response = useGetLevelSensorDataQuery();

  return (
    <RtkQueryGate {...response}>
      <Stack spacing={4} useFlexGap alignItems="center">
        <Stack flexDirection="row" useFlexGap spacing={2} alignItems="center">
          <Text size="title">Level</Text>
          <PillBox gradiantDirection="180deg">
            <Text size="body">{response.data?.level_percent}</Text>
          </PillBox>
        </Stack>
        <LevelData
          rating={response.data?.pitch_rating}
          image={
            <img
              width="80%"
              style={{transform: `rotate(${response.data?.pitch}deg)`}}
              src={van_side}
            />
          }
        >
          <Text size="body">Pitch</Text>
          <Text size="body">{response.data?.pitch}</Text>
        </LevelData>
        <LevelData
          rating={response.data?.roll_rating}
          image={
            <img
              width="55%"
              style={{transform: `rotate(${response.data?.roll}deg)`}}
              src={van_front}
            />
          }
        >
          <Text size="body">Roll</Text>
          <Text size="body">{response.data?.roll}</Text>
        </LevelData>
      </Stack>
    </RtkQueryGate>
  );
};

export default LevelSensor;
