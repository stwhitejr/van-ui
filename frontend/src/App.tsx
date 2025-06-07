import {createTheme, ThemeProvider} from '@mui/material/styles';
import {store} from '@root/store';
import {Provider} from 'react-redux';
import Toast from '@root/features/toast/Toast';
import './App.css';
import Pages from './Pages';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

const App = () => {
  return (
    <ThemeProvider theme={darkTheme}>
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
