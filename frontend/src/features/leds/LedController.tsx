import {Box, Grid2, Slider, Stack, TextField} from '@mui/material';
import Button from '@root/components/Button';
import PillBox from '@root/components/PillBox';
import Text from '@root/components/Text';
import {useEffect, useState} from 'react';
import {useConfigureLedsMutation} from './api';
import {RgbColor, RgbColorPicker} from 'react-colorful';
import './LedController.css';

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

  const rgbValue = Object.values(color).join(', ');

  useEffect(() => {
    api({
      on,
      brightness,
      sleep,
      color: rgbValue,
    });
  }, [api, brightness, color, on, sleep]);

  return (
    <Grid2 container spacing={2} width="100%" p={5}>
      <Grid2 size={4}>
        <Stack spacing={2}>
          <Button onClick={() => setOn(!on)}>
            <Text size="large">Power</Text>
          </Button>
          <RgbColorPicker color={color} onChange={setColor} />
          <Text size="large">{rgbValue}</Text>
        </Stack>
      </Grid2>

      <Grid2 size={8}>
        <Stack spacing={2}>
          <PillBox>
            <Box pb={1}>
              <Text size="small">Sleep</Text>
            </Box>
            <TextField
              value={sleep}
              onChange={(_, newValue) => setSleep(newValue)}
              type="number"
              fullWidth
            />
          </PillBox>
          <PillBox>
            <Text size="small">Brightness</Text>
            <Slider
              value={brightness}
              onChange={(_, newValue) => setBrightness(newValue)}
              min={0}
              max={100}
              step={1}
              valueLabelDisplay="auto"
            />
          </PillBox>
          <Button onClick={() => {}}>
            <Text size="large">Preset 1</Text>
          </Button>
        </Stack>
      </Grid2>
    </Grid2>
  );
};

export default LedController;
