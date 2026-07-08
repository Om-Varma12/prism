import axios from 'axios';

// Simple in-memory cache for API responses
const cache = new Map<string, any>();

// Generate cache key from method, URL, and params
function getCacheKey(method: string, url: string, params?: any): string {
  const paramsStr = params ? JSON.stringify(params) : '';
  return `${method}:${url}:${paramsStr}`;
}

export const apiClient = axios.create({
  baseURL: 'http://localhost:3001',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor: check cache before making API call
apiClient.interceptors.request.use((config) => {
  // Only cache GET requests
  if (config.method?.toLowerCase() === 'get') {
    // Skip caching for alerts endpoint (real-time data)
    if (!config.url?.includes('/alerts')) {
      const cacheKey = getCacheKey(config.method || 'get', config.url || '', config.params);
      const cachedResponse = cache.get(cacheKey);
      
      if (cachedResponse) {
        console.log(`[Cache HIT] ${config.url}`);
        // Return cached response immediately
        return Promise.reject({
          _cached: true,
          data: cachedResponse,
          config,
        });
      } else {
        console.log(`[Cache MISS] ${config.url}`);
      }
    }
  }
  return config;
});

// Response interceptor: store successful responses in cache
apiClient.interceptors.response.use(
  (res) => {
    // Cache successful GET responses (except alerts)
    if (res.config.method?.toLowerCase() === 'get' && !res.config.url?.includes('/alerts')) {
      const cacheKey = getCacheKey(res.config.method || 'get', res.config.url || '', res.config.params);
      cache.set(cacheKey, res.data);
      console.log(`[Cache STORE] ${res.config.url}`);
    }
    return res;
  },
  (err) => {
    // Handle cached response from request interceptor
    if (err._cached) {
      // Return cached data as if it was a successful response
      return Promise.resolve({ data: err.data, config: err.config, status: 200 });
    }
    console.error('[API Error]', err.response?.status, err.config?.url, err.response?.data);
    return Promise.reject(err);
  }
);
