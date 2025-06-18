import RtkQueryGate from '@root/components/RtkQueryGate';
import {LevelRating, useGetLevelSensorDataQuery} from './api';
import {Box, Stack} from '@mui/material';
import Text from '@root/components/Text';
import PillBox from '@root/components/PillBox';
import {ComponentProps, ReactNode} from 'react';
import van_front from '@root/assets/images/van_front.png';
import van_side from '@root/assets/images/van_side.png';
import Container from '@root/components/Container';
import {RefreshIcon} from '@root/components/icons';

const colorByRating = {
  Good: 'linear-gradient(0deg, #2ca650 0%,rgb(103, 216, 137) 100%)',
  Okay: 'linear-gradient(0deg, #c0972e 0%,rgb(234, 197, 104) 100%)',
  Bad: 'linear-gradient(0deg, #9a3434 0%,rgb(203, 96, 96) 100%)',
};

const LevelData = ({
  image,
  rotateStyle,
  children,
  rating,
}: {
  image: ReactNode;
  children: ReactNode;
  rating: LevelRating;
  rotateStyle: ComponentProps<typeof Box>['sx'];
}) => {
  return (
    <Stack spacing={2} useFlexGap alignItems="center" width="50%">
      <Box width="90%" textAlign="center" position="relative">
        <Box sx={{...rotateStyle}}>{image}</Box>
        <Box
          sx={{
            position: 'absolute',
            opacity: '.3',
            zIndex: 2,
            top: 0,
          }}
        >
          {image}
        </Box>
      </Box>
      <PillBox
        gradiantDirection="180deg"
        sx={{
          width: '100%',
          display: 'flex',
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
          <Box
            sx={{p: 1, borderRadius: '100%', background: colorByRating[rating]}}
          />
          {children}
        </Stack>
      </PillBox>
    </Stack>
  );
};

const LevelSensor = () => {
  const response = useGetLevelSensorDataQuery(undefined, {
    pollingInterval: 15000,
  });

  return (
    <Container
      title="Level"
      additional={
        <Stack alignItems="center" flexDirection="row" useFlexGap spacing={2}>
          <Box sx={{cursor: 'pointer'}} onClick={() => response.refetch()}>
            <RefreshIcon />
          </Box>
          <PillBox gradiantDirection="180deg">
            <Text size="body">{response.data?.level_percent}%</Text>
          </PillBox>
        </Stack>
      }
    >
      <RtkQueryGate {...response}>
        <Stack spacing={4} useFlexGap alignItems="center">
          <LevelData
            rating={response.data?.pitch_rating}
            image={<img width="80%" src={van_side} />}
            rotateStyle={{transform: `rotate(${response.data?.pitch}deg)`}}
          >
            <Text size="body">Pitch</Text>
            <Text size="body">{response.data?.pitch}</Text>
          </LevelData>
          <LevelData
            rating={response.data?.roll_rating}
            image={<img width="55%" src={van_front} />}
            rotateStyle={{transform: `rotate(${response.data?.roll}deg)`}}
          >
            <Text size="body">Roll</Text>
            <Text size="body">{response.data?.roll}</Text>
          </LevelData>
        </Stack>
      </RtkQueryGate>
    </Container>
  );
};

export default LevelSensor;
