import Text from './Text';

export interface ErrorProps {
  message: string;
}

const Error = (props: ErrorProps) => {
  return <Text size="large">Error: {props.message}</Text>;
};

export default Error;
