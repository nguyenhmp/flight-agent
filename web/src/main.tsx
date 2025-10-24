import React from 'react'
import ReactDOM from 'react-dom/client'
// 1. Import your Watches page
import Watches from './pages/Watches' 

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* 2. Render the Watches page */}
    <Watches />
  </React.StrictMode>,
)