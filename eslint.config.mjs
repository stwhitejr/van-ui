import { defineConfig } from 'eslint/config';
import ts from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import prettierConfig from 'eslint-config-prettier';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import prettier from 'eslint-plugin-prettier';

export default defineConfig([
  prettierConfig,
  {
    files: ['**/*.ts', '**/*.tsx', '**/*.js'],
    languageOptions: {
      parser: tsParser,
    },
    plugins: { '@typescript-eslint': ts, react, reactHooks, prettier },
    rules: {
      '@typescript-eslint/no-unused-vars': 'warn',
      'no-var': 'error', // Enforce let/const instead of var
      'prefer-const': 'warn', // Suggest using const when possible
      eqeqeq: ['error', 'always'], // Require strict equality (=== and !==)
      'no-console': 'warn', // Warn on console logs (you can change to "error" in production)
      'no-debugger': 'error', // Disallow debugger statements
      curly: ['error', 'all'], // Enforce curly braces on control statements
      'no-unused-vars': 'warn', // Warn about unused variables
      'no-empty-function': 'warn', // Warn about empty functions

      '@typescript-eslint/no-explicit-any': 'warn', // Discourage using 'any'
      '@typescript-eslint/explicit-function-return-type': 'off', // Consider requiring explicit return types
      '@typescript-eslint/no-non-null-assertion': 'error', // Avoid using the non-null assertion (!)

      'react/jsx-uses-react': 'off', // No longer needed with React 17+
      'react/react-in-jsx-scope': 'off', // No longer needed with React 17+
      'react/jsx-boolean-value': ['error', 'never'], // Enforce boolean shorthand (e.g., <Component disabled /> instead of <Component disabled={true} />)
      'reactHooks/rules-of-hooks': 'error', // Enforce the rules of hooks
      'reactHooks/exhaustive-deps': 'warn', // Ensure dependencies are listed correctly in useEffect

      'prettier/prettier': 'warn', // Show Prettier issues as warnings
    },
  },
]);
