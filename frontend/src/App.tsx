import {createTheme, ThemeProvider} from '@mui/material/styles';
import {store} from '@root/store';
import {Provider} from 'react-redux';
import Toast from '@root/features/toast/Toast';
import './App.css';
import Pages from './Pages';

export const theme = createTheme({
  palette: {
    mode: 'dark',
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 480,
      md: 800,
      lg: 1200,
      xl: 1536,
    },
  },
});

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <div id="App">
        <Provider store={store}>
          <Pages />
          <Toast />
        </Provider>
      </div>
    </ThemeProvider>
  );
};

export default App;
