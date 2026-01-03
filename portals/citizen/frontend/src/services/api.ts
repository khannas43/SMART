import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import toast from 'react-hot-toast';

// Get base URL from environment or use default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8081/citizen/api/v1';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token to requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add language header if available
    const language = localStorage.getItem('i18nextLng') || 'en';
    if (config.headers) {
      config.headers['Accept-Language'] = language;
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response) {
      // Handle different HTTP status codes
      switch (error.response.status) {
        case 401:
          // Unauthorized - clear tokens but don't redirect here
          // Let the component handle navigation to avoid full page reload
          localStorage.removeItem('auth_token');
          localStorage.removeItem('refresh_token');
          // Don't redirect here - let components handle it via React Router
          // window.location.href causes full page reload and breaks Vite routing
          break;
        case 403:
          toast.error('Access denied. You do not have permission to perform this action.');
          break;
        case 404:
          // Don't show toast for 404 errors - let components handle them
          // toast.error('Resource not found.');
          break;
        case 500:
          // Don't show toast for optional endpoints that may not be implemented yet
          const url = error.config?.url || '';
          const optionalEndpoints = [
            '/family/benefits',
            '/consent/preferences',
            '/ml/suggested-relations',
            '/audit/timeline',
            '/applications/', // Application history endpoint is optional
            '/feedback/', // Feedback endpoint may return 500 if not fully implemented
          ];
          const isOptionalEndpoint = optionalEndpoints.some(endpoint => url.includes(endpoint));
          // Check specifically for history endpoint
          const isHistoryEndpoint = url.includes('/history');
          if (!isOptionalEndpoint && !isHistoryEndpoint) {
            toast.error('Server error. Please try again later.');
          }
          break;
        default:
          const message = (error.response.data as { message?: string })?.message || 'An error occurred';
          toast.error(message);
      }
    } else if (error.request) {
      // Request made but no response received
      toast.error('Network error. Please check your connection.');
    } else {
      // Something else happened
      toast.error('An unexpected error occurred.');
    }

    return Promise.reject(error);
  }
);

export default apiClient;

