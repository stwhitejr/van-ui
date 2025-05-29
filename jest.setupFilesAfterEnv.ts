import '@testing-library/jest-dom';
import 'jest-environment-jsdom';
import {setupServer} from 'msw/node';
import handlers from './src/mocks/handlers';

// Note: This can get taxing if you have a lot of tests
// It may be better to setup the server for each test with only the handlers you need
const server = setupServer(...handlers);
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
