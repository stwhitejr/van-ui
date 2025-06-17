import {ComponentProps, ReactNode} from 'react';
import PillBox from './PillBox';
import {Box} from '@mui/material';

export interface ButtonProps {
  children: ReactNode;
  onClick: () => void;
  isActive?: boolean;
  sx?: ComponentProps<typeof Box>['sx'];
}

const Button = (props: ButtonProps) => {
  return (
    <Box
      sx={{
        ...props.sx,
        cursor: 'pointer',
      }}
      onClick={() => props.onClick()}
    >
      <PillBox
        gradiantVariation={props.isActive ? 'activeButton' : 'button'}
        gradiantDirection="180deg"
        sx={{
          textAlign: 'center',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {props.children}
      </PillBox>
    </Box>
  );
};

export default Button;
