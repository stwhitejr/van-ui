import {ReactNode} from 'react';
import PillBox from './PillBox';

export interface ButtonProps {
  children: ReactNode;
  onClick: () => void;
}

const Button = (props: ButtonProps) => {
  return (
    <div
      style={{cursor: 'pointer', height: '100%'}}
      onClick={() => props.onClick()}
    >
      <PillBox
        gradiantVariation="button"
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
    </div>
  );
};

export default Button;
