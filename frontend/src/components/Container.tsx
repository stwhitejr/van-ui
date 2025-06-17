import {Box, Stack} from '@mui/material';
import {ReactNode} from 'react';
import Text from './Text';

export interface ContainerProps {
  children: ReactNode;
  title: ReactNode;
  additional?: ReactNode;
}

const Container = (props: ContainerProps) => {
  return (
    <Box
      borderRadius="10px"
      p={2}
      sx={{
        background:
          'linear-gradient(180deg, rgba(116, 116, 116, 0.1) 50%, #121112 100%)',
      }}
    >
      <Stack
        flexDirection="row"
        justifyContent="space-between"
        alignItems="center"
      >
        <Text size="large">{props.title}</Text>
        {props.additional}
      </Stack>

      <Box
        sx={{
          p: 2,
        }}
      >
        {props.children}
      </Box>
    </Box>
  );
};

export default Container;
