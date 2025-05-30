import type {Preview} from '@storybook/react';
import {initialize, mswDecorator} from 'msw-storybook-addon';
import handlers from '../src/mocks/handlers';

initialize({
  onUnhandledRequest: 'warn',
  serviceWorker: {
    url: '/mockServiceWorker.js',
  },
});

export const decorators = [mswDecorator];

const preview: Preview = {
  parameters: {
    msw: {handlers},
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
};

export default preview;
