import {renderStory, screen} from '@root/util/test_util';
import * as stories from '../SnowboardsListPage.stories';

describe('Snowboards Features: List', () => {
  beforeEach(() => {
    renderStory(stories.SnowboardsListPageDemo, stories.default);
  });
  it('should render api response', async () => {
    expect(await screen.findByText('Yes')).toBeInTheDocument();
  });
});
