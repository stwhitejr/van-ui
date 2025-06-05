import {Box} from '@mui/material';
import {ComponentProps, ReactNode} from 'react';

export interface PillBoxProps extends ComponentProps<typeof Box> {
  children: ReactNode;
  gradiantDirection?: string;
  gradiantVariation?: 'default' | 'button' | 'on';
}

const gradiantByVariation = {
  default: ' #38343c 0%, #211f23 100%',
  button: ' #38343c 0%, #211f23 100%',
  on: ' #c29945 0%, #e2b65b 100%',
};

const PillBox = ({
  gradiantDirection = '90deg',
  gradiantVariation = 'default',
  children,
  ...props
}: PillBoxProps) => {
  return (
    <Box
      sx={{
        p: 1,
        borderRadius: '10px',
        background: `linear-gradient(${gradiantDirection}, ${gradiantByVariation[gradiantVariation]})`,
        ...(gradiantVariation === 'button'
          ? {
              '&:hover, &:focus': {
                background: `linear-gradient(0deg, #37323c 0%, #665f70 100%)`,
              },
            }
          : {}),
        ...props.sx,
      }}
    >
      {children}
    </Box>
  );
};

export default PillBox;
