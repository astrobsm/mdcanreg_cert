/**
 * Configuration file for MDCAN BDM 2025 Certificate Platform
 * Contains environment-specific API URLs and settings
 */

const ENV = process.env.NODE_ENV || 'development';

// Check if running in Docker
const isDocker = process.env.REACT_APP_DOCKER === 'true';

const config = {
  development: {
    // If running in Docker, backend is at 'backend' host, otherwise localhost:8080
    API_URL: isDocker ? 'http://backend:8080' : 'http://localhost:8080',
    DEBUG: true,
    TIMEOUT: 10000, // 10 seconds
  },
  test: {
    API_URL: 'http://localhost:8080',
    DEBUG: true,
    TIMEOUT: 5000, // 5 seconds
  },
  production: {
    // Backend is hosted on Digital Ocean
    API_URL: 'https://mdcanbdm042-2025-tdlv8.ondigitalocean.app',
    DEBUG: false,
    TIMEOUT: 30000, // 30 seconds
  }
};

// For browser environment, we should always use localhost for local development
if (typeof window !== 'undefined') {
  const hostname = window.location.hostname;
  
  // In browser and in development, but hostname isn't localhost
  if (ENV === 'development' && hostname !== 'localhost' && hostname !== '127.0.0.1') {
    // We're probably running in Docker but from browser perspective,
    // so use the container hostname from browser perspective
    config.development.API_URL = `http://${hostname}:5000`;
  }
}

// Export the configuration based on current environment
export default config[ENV];
