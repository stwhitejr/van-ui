import SnowboardsListPage from '@root/pages/SnowboardsListPage';
import {store} from '@root/store';
import {Provider} from 'react-redux';
import {BrowserRouter, Route, Routes} from 'react-router-dom';
import {snowboardPath, snowboardsPath} from './paths';
import SnowboardUpdatePage from './pages/SnowboardUpdatePage';
import Toast from '@root/features/toast/Toast';

const App = () => {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <Routes>
          <Route
            path={snowboardsPath.pattern}
            element={<SnowboardsListPage />}
          />
          <Route
            path={snowboardPath.pattern}
            element={<SnowboardUpdatePage />}
          />
        </Routes>
      </BrowserRouter>
      <Toast />
    </Provider>
  );
};

export default App;
