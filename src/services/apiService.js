/**
 * Optimized API service for MDCAN BDM 2025 Certificate Platform
 * Implements caching, request cancellation, and error handling
 */

import axios from 'axios';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8080',
  timeout: 15000, // 15 second timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request interceptor for adding auth tokens, timestamps, etc.
apiClient.interceptors.request.use(
  config => {
    // Add timestamp to GET requests to prevent caching issues
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      };
    }
    
    // Add other request interceptors here
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor for global error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Handle network errors
    if (!error.response) {
      console.error('Network Error:', error.message);
      return Promise.reject({
        message: 'Network error. Please check your internet connection.'
      });
    }
    
    // Handle specific HTTP status codes
    switch (error.response.status) {
      case 401:
        console.error('Authentication Error:', error.response.data);
        // Handle unauthorized access
        break;
      case 403:
        console.error('Authorization Error:', error.response.data);
        // Handle forbidden access
        break;
      case 404:
        console.error('Resource Not Found:', error.response.data);
        // Handle not found
        break;
      case 429:
        console.error('Rate Limit Exceeded:', error.response.data);
        // Handle rate limiting
        break;
      case 500:
        console.error('Server Error:', error.response.data);
        // Handle server errors
        break;
      default:
        console.error(`HTTP Error ${error.response.status}:`, error.response.data);
    }
    
    return Promise.reject(error.response.data);
  }
);

// Simple in-memory cache
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

// API service with cached methods
export const apiService = {
  // GET request with caching
  async get(url, params = {}, useCache = true) {
    const cacheKey = `${url}?${JSON.stringify(params)}`;
    
    // Return cached data if available and not expired
    if (useCache && cache.has(cacheKey)) {
      const cachedData = cache.get(cacheKey);
      if (Date.now() - cachedData.timestamp < CACHE_DURATION) {
        return Promise.resolve(cachedData.data);
      }
      // Clear expired cache
      cache.delete(cacheKey);
    }
    
    try {
      const response = await apiClient.get(url, { params });
      
      // Cache the response if caching is enabled
      if (useCache) {
        cache.set(cacheKey, {
          timestamp: Date.now(),
          data: response.data
        });
      }
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Clear all cache or specific cache entry
  clearCache(url = null, params = {}) {
    if (url) {
      const cacheKey = `${url}?${JSON.stringify(params)}`;
      cache.delete(cacheKey);
    } else {
      cache.clear();
    }
  },
  
  // POST request
  async post(url, data = {}) {
    try {
      const response = await apiClient.post(url, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // PUT request
  async put(url, data = {}) {
    try {
      const response = await apiClient.put(url, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // DELETE request
  async delete(url) {
    try {
      const response = await apiClient.delete(url);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Request with cancellation support (for search, etc)
  createCancellableRequest() {
    const source = axios.CancelToken.source();
    
    return {
      execute: (config) => {
        return apiClient({
          ...config,
          cancelToken: source.token
        });
      },
      cancel: (message = 'Request cancelled') => {
        source.cancel(message);
      }
    };
  }
};

export default apiService;
