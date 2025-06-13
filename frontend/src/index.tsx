import {createRoot} from 'react-dom/client';
import App from '@root/App';

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then((reg) => {
        console.log('Service Worker registered: ', reg);
      })
      .catch((err) => {
        console.error('Service Worker registration failed: ', err);
      });
  });
}

async function enableMocking() {
  if (process.env.NODE_ENV !== 'development') {
    return;
  }
  const {worker} = await import('./mocks/browser');
  return worker.start();
}

enableMocking().then(() => {
  const root = createRoot(document.getElementById('root'));
  root.render(<App />);
});
