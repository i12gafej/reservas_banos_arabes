declare module 'reactive-button' {
  import * as React from 'react';

  export type ButtonState = 'idle' | 'loading' | 'success' | 'error';

  export interface ReactiveButtonProps {
    buttonState?: ButtonState;
    onClick?: React.MouseEventHandler<HTMLButtonElement>;
    color?:
      | 'primary'
      | 'secondary'
      | 'teal'
      | 'green'
      | 'red'
      | 'violet'
      | 'blue'
      | 'yellow'
      | 'dark'
      | 'light';
    idleText?: React.ReactNode;
    loadingText?: React.ReactNode;
    successText?: React.ReactNode;
    errorText?: React.ReactNode;
    className?: string;
    style?: React.CSSProperties;
    [key: string]: any;
  }

  const ReactiveButton: React.FC<ReactiveButtonProps>;
  export default ReactiveButton;
} 