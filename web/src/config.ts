// This file centralizes configuration like API endpoints.

// Get the API URL from environment variables,
// falling back to localhost:8000 for development.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export { API_URL };