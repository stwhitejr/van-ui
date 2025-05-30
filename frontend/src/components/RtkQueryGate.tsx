import Loading from './Loading';
import Error from './Error';
import {ReactNode} from 'react';
import {SerializedError} from '@reduxjs/toolkit';
import {FetchBaseQueryError} from '@reduxjs/toolkit/query';

export interface RtkQueryGateProps {
  children: ReactNode;
  isLoading?: boolean;
  error?: SerializedError | FetchBaseQueryError;
}

const RtkQueryGate = (props: RtkQueryGateProps) => {
  if (props.isLoading) {
    return <Loading />;
  }
  if (props.error) {
    // @ts-ignore todo: address
    return <Error message={props.error.message} />;
  }
  return <div>{props.children}</div>;
};

export default RtkQueryGate;
