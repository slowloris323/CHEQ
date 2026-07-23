import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Auth0Provider } from '@auth0/auth0-react'
import './index.css'
import App from './App.jsx'

const domain = import.meta.env.VITE_AUTH0_DOMAIN
const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID
const audience = import.meta.env.VITE_AUTH0_AUDIENCE
const redirectUri = import.meta.env.VITE_AUTH0_REDIRECT_URI

const onRedirectCallback = (appState) => {
  if (appState && appState.resourceUri) {
    const url = new URL(window.location.origin)
    url.searchParams.set('resource_uri', appState.resourceUri)
    window.history.replaceState({}, document.title, url.toString())
    window.dispatchEvent(new PopStateEvent('popstate'))
  } else {
    window.history.replaceState({}, document.title, window.location.pathname)
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: redirectUri || window.location.origin,
        audience: audience,
      }}
      onRedirectCallback={onRedirectCallback}
      useRefreshTokens={true}
      cacheLocation="localstorage"
    >
      <App />
    </Auth0Provider>
  </StrictMode>,
)
