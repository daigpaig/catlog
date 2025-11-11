const getApiBaseUrl = (): string => {
  if (import.meta.env.DEV) {
    return 'http://localhost:8000';
  }
  
  const replitDomain = window.location.hostname;
  return `https://${replitDomain.replace(/^[^.]+/, (match) => match + '-8000')}`;
};

export const API_BASE_URL = getApiBaseUrl();
