import {store} from '@root/store';
import {Provider} from 'react-redux';
import Toast from '@root/features/toast/Toast';
import './App.css';
import Pages from './Pages';

const App = () => {
  return (
    <div id="App">
      <Provider store={store}>
        <Pages />
        <Toast />
      </Provider>
    </div>
  );
};

export default App;
