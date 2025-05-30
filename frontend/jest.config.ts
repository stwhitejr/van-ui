import {JestConfigWithTsJest} from 'ts-jest';
import 'cross-fetch/polyfill';

const config: JestConfigWithTsJest = {
  preset: 'ts-jest',
  testEnvironment: 'jest-fixed-jsdom',
  setupFiles: ['<rootDir>/jest.setupFiles.ts'],
  setupFilesAfterEnv: ['<rootDir>/jest.setupFilesAfterEnv.ts'],
  moduleNameMapper: {
    '@root/(.*)': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': '<rootDir>/jest.mock.js',
  },
};

export default config;
