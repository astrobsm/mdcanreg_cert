import React from 'react';
import ReactDOM from 'react-dom/client';
import './setupProduction'; // Import setup file to fix variable hoisting issues
import './index.css';
import './optimizations.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
