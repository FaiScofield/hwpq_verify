import './styles.css';

import { createAppShell } from './app/app-shell';

const app = document.querySelector<HTMLDivElement>('#app');

if (!app) {
  throw new Error('Missing #app mount node');
}

app.append(createAppShell());
