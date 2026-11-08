import '@fontsource/overpass/400.css'
import '@fontsource/overpass/600.css'
import '@fontsource/overpass/800.css'
import '@fontsource/overpass/900.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
