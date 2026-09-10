// Central API & WebSocket configuration for local and GitHub Pages deployment

export const getApiBase = () => {
  // If hosted on GitHub Pages or custom external static domain, target local backend
  if (typeof window !== 'undefined' && window.location.hostname.includes('github.io')) {
    return 'http://127.0.0.1:8000';
  }
  return '';
};

export const getWsUrl = () => {
  if (typeof window !== 'undefined' && window.location.hostname.includes('github.io')) {
    return 'ws://127.0.0.1:8000/ws/telemetry';
  }
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = window.location.host || '127.0.0.1:8000';
  return `${wsProtocol}//${wsHost}/ws/telemetry`;
};
