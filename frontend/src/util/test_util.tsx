import {store} from '@root/store';
import {composeStory} from '@storybook/react';
import * as testingLibrary from '@testing-library/react';
import {ReactNode} from 'react';
import {Provider} from 'react-redux';
import {MemoryRouter} from 'react-router-dom';
import {ComponentAnnotations, StoryAnnotations} from 'storybook/internal/types';

const customRender = (
  node: ReactNode,
  options?: {store?: typeof store; routePath?: string}
) => {
  testingLibrary.render(
    <Provider store={options?.store || store}>
      <MemoryRouter
        initialEntries={options?.routePath ? [options.routePath] : []}
      >
        {node}
      </MemoryRouter>
    </Provider>
  );
};

const renderStory = (
  story: StoryAnnotations,
  meta: ComponentAnnotations,
  props = {}
) => {
  const Component = composeStory(story, meta);
  testingLibrary.render(<Component {...props} />);
};

export * from '@testing-library/react';
export {customRender as render, renderStory};
