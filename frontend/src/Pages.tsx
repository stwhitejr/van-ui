import {Box, Grid2, Stack} from '@mui/material';
import SmartShuntDashboard from '@root/features/smartshunt/SmartShuntDashboard';
import ToggleInverter from '@root/features/inverter/ToggleInverter';
import LevelSensor from '@root/features/level_sensor/LevelSensor';
import './App.css';
import {useState} from 'react';
import LedController from './features/leds/LedController';
import Button from './components/Button';
import Text from './components/Text';
import Container from './components/Container';
import LogoColor from '@root/assets/images/logo3.png';
import {theme} from './App';

const Pages = () => {
  const [pageNumber, setPageNumber] = useState(1);
  return (
    <Box
      sx={{
        display: 'flex',
        minHeight: '100vh',
        width: '100%',
        flexDirection: 'column',
      }}
    >
      <Box
        m={2}
        mb={0}
        bgcolor="rgba(116, 116, 116, 0.1)"
        borderRadius="10px"
        p={1}
        position="relative"
      >
        <Stack
          flexDirection={{
            xs: 'column',
            sm: 'column',
            md: 'row',
          }}
          justifyContent="space-between"
          alignItems="center"
        >
          <Box>
            <Box
              sx={{
                pb: 1,
                [theme.breakpoints.up('md')]: {
                  position: 'absolute',
                  top: '-8px',
                  left: '10px',
                  pb: 0,
                },
              }}
            >
              <img src={LogoColor} width="100px" />
            </Box>
            <Box
              ml={15}
              display={{
                xs: 'none',
                sm: 'none',
                md: 'block',
              }}
            >
              <Text size="large">Van Dashboard</Text>
            </Box>
          </Box>

          <Stack flexDirection="row" spacing={2} useFlexGap alignItems="center">
            <Button
              isActive={pageNumber === 1}
              onClick={() => setPageNumber(1)}
            >
              <Text size="body">Home</Text>
            </Button>
            <Button
              isActive={pageNumber === 2}
              onClick={() => setPageNumber(2)}
            >
              <Text size="body">LEDs</Text>
            </Button>
          </Stack>
        </Stack>
      </Box>
      <Box flex={1}>
        {pageNumber === 1 && (
          <Grid2 container width="100%" alignItems="flex-start">
            <Grid2
              size={{
                xs: 12,
                sm: 12,
                md: 6,
              }}
              p={2}
              pr={0}
              pb={0}
            >
              <LevelSensor />
            </Grid2>
            <Grid2
              size={{
                xs: 12,
                sm: 12,
                md: 6,
              }}
              p={2}
              pb={0}
            >
              <Container title="Battery Monitor">
                <Stack spacing={2}>
                  <SmartShuntDashboard />
                  <ToggleInverter />
                </Stack>
              </Container>
            </Grid2>
          </Grid2>
        )}
        {pageNumber === 2 && <LedController />}
      </Box>
    </Box>
  );
};

export default Pages;
