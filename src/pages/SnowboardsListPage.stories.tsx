import {Provider} from 'react-redux';
import SnowboardsListPage from '@root/pages/SnowboardsListPage';
import type {Meta, StoryObj} from '@storybook/react';
import {store} from '@root/store';
import {MemoryRouter} from 'react-router-dom';

const meta: Meta<typeof SnowboardsListPage> = {
  component: SnowboardsListPage,
  decorators: [
    (Story) => {
      return (
        <Provider store={store}>
          <MemoryRouter>
            <Story />
          </MemoryRouter>
        </Provider>
      );
    },
  ],
};

export default meta;
type Story = StoryObj<typeof SnowboardsListPage>;

export const SnowboardsListPageDemo: Story = {
  args: {},
};
