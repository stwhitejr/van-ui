import {TextField} from '@mui/material';
import PillBox from './PillBox';
import Text from './Text';
import {ComponentProps} from 'react';

export interface TextInputProps extends ComponentProps<typeof TextField> {}

const TextInput = ({label, ...props}: TextInputProps) => {
  return (
    <PillBox>
      <Text size="small">{label}</Text>
      <TextField {...props} />
    </PillBox>
  );
};

export default TextInput;
