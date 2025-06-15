import {
  Box,
  FormControl,
  Grid2,
  InputLabel,
  MenuItem,
  Select,
  Slider,
  Stack,
} from '@mui/material';
import Button from '@root/components/Button';
import PillBox from '@root/components/PillBox';
import Text from '@root/components/Text';
import {useEffect, useMemo, useRef, useState} from 'react';
import {
  LedConfigureRequest,
  LedResponse,
  useConfigureLedsMutation,
  useLedsStatusQuery,
} from './api';
import {RgbColor, RgbColorPicker} from 'react-colorful';
import './LedController.css';
import useDebounce from '@root/util/useDebounce';
import Container from '@root/components/Container';
import RtkQueryGate from '@root/components/RtkQueryGate';

const LedControllerForm = ({data}: {data: LedResponse}) => {
  const isFirstMount = useRef(true);
  const [api] = useConfigureLedsMutation();

  // Use API response as initial data
  // Note: this can become stale if the LEDs change elsewhere like the voice commands
  const [on, setOn] = useState(data.on || false);
  const [sleep, setSleep] = useState(0);
  const [brightness, setBrightness] = useState(data.brightness || 50);
  const [color, setColor] = useState<RgbColor>(
    data.color
      ? {
          r: data.color[0],
          g: data.color[1],
          b: data.color[2],
        }
      : {
          r: 255,
          g: 255,
          b: 255,
        }
  );
  const [preset, setPreset] = useState<null | LedConfigureRequest['preset']>(
    null
  );

  const memoizedValue = useMemo(
    () => ({
      on,
      brightness,
      sleep,
      color: Object.values(color).join(', '),
      preset,
    }),
    [on, brightness, sleep, color, preset]
  );

  const debouncedValue = useDebounce(memoizedValue, 500);

  useEffect(() => {
    if (isFirstMount.current) {
      isFirstMount.current = false;
    } else {
      api(debouncedValue);
    }
  }, [api, debouncedValue]);

  return (
    <Grid2 container spacing={2} width="100%" p={2}>
      <Grid2 size={{xs: 6, sm: 6, md: 1}}>
        <Button
          onClick={() => setOn(!on)}
          sx={{
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
          }}
        >
          <Text size="large">{on ? 'Off' : 'On'}</Text>
        </Button>
      </Grid2>
      <Grid2 size={{xs: 6, sm: 6, md: 3}}>
        <PillBox
          sx={{
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <FormControl variant="filled" fullWidth>
            <InputLabel id="demo-simple-select-label">Sleep</InputLabel>
            <Select
              labelId="demo-simple-select-label"
              value={sleep}
              label="Sleep"
              // @ts-ignore
              onChange={({target: {value}}) => setSleep(value)}
            >
              <MenuItem value={0}>None</MenuItem>
              <MenuItem value={300000}>5 Minutes</MenuItem>
              <MenuItem value={1800000}>30 Minutes</MenuItem>
              <MenuItem value={3600000}>1 Hour</MenuItem>
              <MenuItem value={7200000}>2 Hours</MenuItem>
            </Select>
          </FormControl>
        </PillBox>
      </Grid2>

      <Grid2 size={{xs: 12, sm: 12, md: 8}} display="flex">
        <PillBox
          gradiantDirection="-90deg"
          sx={{
            display: 'flex',
            flex: 1,
            alignItems: 'center',
          }}
        >
          <Box flex={1}>
            <Text size="small">Brightness</Text>
            <Slider
              value={brightness}
              onChange={(_, newValue) => setBrightness(newValue)}
              min={0}
              max={100}
              step={1}
              valueLabelDisplay="auto"
            />
          </Box>
        </PillBox>
      </Grid2>
      <Grid2 size={{xs: 12, sm: 12, md: 4}} textAlign="center">
        <RgbColorPicker color={color} onChange={setColor} />
        <Text size="large">{memoizedValue.color}</Text>
      </Grid2>

      <Grid2 size={{xs: 12, sm: 12, md: 8}}>
        <Container
          title="Presets"
          additional={
            !!preset && (
              <Box
                sx={{
                  textDecoration: 'underline',
                  cursor: 'pointer',
                }}
                onClick={() => setPreset(null)}
              >
                <Text size="small">Remove Preset</Text>
              </Box>
            )
          }
        >
          <Stack spacing={2}>
            <Button
              isActive={preset === 'rainbow'}
              onClick={() => setPreset('rainbow')}
            >
              <Text size="large">Rainbow</Text>
            </Button>
            <Button
              isActive={preset === 'chase'}
              onClick={() => setPreset('chase')}
            >
              <Text size="large">Chase</Text>
            </Button>
            <Button
              isActive={preset === 'pulse'}
              onClick={() => setPreset('pulse')}
            >
              <Text size="large">Pulse</Text>
            </Button>
          </Stack>
        </Container>
      </Grid2>
    </Grid2>
  );
};

const LedController = () => {
  const statusResponse = useLedsStatusQuery();

  return (
    <RtkQueryGate {...statusResponse}>
      {statusResponse.data && <LedControllerForm data={statusResponse.data} />}
    </RtkQueryGate>
  );
};

export default LedController;
