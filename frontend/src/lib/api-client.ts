import axios from 'axios';

// Use environment variable for API URL, fallback to localhost:3001 (backend port)
const getBaseURL = () => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  // Backend always runs on port 3001
  return 'http://localhost:3001';
};

export const apiClient = axios.create({
  baseURL: getBaseURL(),
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('[API Error]', err.response?.status, err.config?.url, err.response?.data);
    return Promise.reject(err);
  }
);
