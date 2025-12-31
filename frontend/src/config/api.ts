const getApiBaseUrl = (): string => {
  // Use environment variable if set, otherwise default to localhost
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Development default
  return import.meta.env.DEV 
    ? 'http://localhost:8000'
    : 'http://localhost:8000'; // Change this to your production API URL
};

export const API_BASE_URL = getApiBaseUrl();
