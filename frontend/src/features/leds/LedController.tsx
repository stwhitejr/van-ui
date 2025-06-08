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
import {useEffect, useMemo, useState} from 'react';
import {LedConfigureRequest, useConfigureLedsMutation} from './api';
import {RgbColor, RgbColorPicker} from 'react-colorful';
import './LedController.css';
import useDebounce from '@root/util/useDebounce';
import Container from '@root/components/Container';

const LedController = () => {
  const [api] = useConfigureLedsMutation();
  const [on, setOn] = useState(false);
  const [sleep, setSleep] = useState(0);
  const [brightness, setBrightness] = useState(50);
  const [color, setColor] = useState<RgbColor>({
    r: 255,
    g: 255,
    b: 255,
  });
  const [preset, setPreset] = useState<null | LedConfigureRequest['preset']>(
    null
  );

  const memoizedValue = useMemo(
    () => ({
      on,
      brightness,
      sleep,
      color: Object.values(color).join(', '),
    }),
    [on, brightness, sleep, color]
  );

  const debouncedValue = useDebounce(memoizedValue, 500);

  useEffect(() => {
    api(debouncedValue);
  }, [api, debouncedValue]);

  return (
    <Grid2 container spacing={2} width="100%" p={2}>
      <Grid2 size={1}>
        <Button height="100%" onClick={() => setOn(!on)}>
          <Text size="large">{on ? 'Off' : 'On'}</Text>
        </Button>
      </Grid2>
      <Grid2 size={3}>
        <PillBox
          sx={{
            height: '100%',
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

      <Grid2 size={8}>
        <PillBox
          gradiantDirection="-90deg"
          sx={{height: '100%', display: 'flex', alignItems: 'center'}}
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
      <Grid2 size={4} pt={2} textAlign="center">
        <RgbColorPicker color={color} onChange={setColor} />
        <Text size="large">{memoizedValue.color}</Text>
      </Grid2>

      <Grid2 size={8} pt={2}>
        <Container title="Presets">
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
            </Button>{' '}
            {!!preset && (
              <Button onClick={() => setPreset(null)}>
                <Text size="large">Remove Preset</Text>
              </Button>
            )}
          </Stack>
        </Container>
      </Grid2>
    </Grid2>
  );
};

export default LedController;
