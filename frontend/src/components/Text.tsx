import {Box} from '@mui/material';
import {ReactNode} from 'react';

const styleBySize = {
  title: {
    fontSize: '2rem',
    fontFamily: 'DM Sans Thin',
  },
  large: {
    fontSize: '1.5rem',
    fontFamily: 'DM Sans Thin',
  },
  body: {
    fontSize: '1rem',
  },
  small: {
    fontSize: '.8rem',
  },
};

export interface TextProps {
  children: ReactNode;
  size: 'title' | 'large' | 'body' | 'small';
}

const Text = (props: TextProps) => {
  return (
    <Box
      sx={{
        color: '#fff9ee',
        ...styleBySize[props.size],
      }}
    >
      {props.children}
    </Box>
  );
};

export default Text;
