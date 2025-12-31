/**
 * API Configuration
 * Centralized API URL configuration for development and production
 */

const getApiUrl = (): string => {
  // In browser/client-side: use NEXT_PUBLIC_ prefix
  if (typeof window !== 'undefined') {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  
  // Server-side: can use different URL if needed
  return process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

export const API_URL = getApiUrl();

// API endpoint helpers
export const API_ENDPOINTS = {
  // User endpoints
  users: {
    classify: `${API_URL}/api/v1/users/classify`,
    latestPlan: (clerkUserId: string) => `${API_URL}/api/v1/users/plans/latest?clerk_user_id=${clerkUserId}`,
  },
  
  // Classification endpoints
  classify: {
    bodyType: `${API_URL}/api/v1/classify/body-type`,
    health: `${API_URL}/api/v1/classify/health`,
  },
  
  // Agent endpoints
  agents: {
    generateRecommendations: `${API_URL}/agents/recommendations/generate`,
    streamRecommendations: `${API_URL}/agents/recommendations/stream`,
    health: `${API_URL}/agents/health`,
  },
  
  // RAG endpoints (if needed in frontend)
  rag: {
    diet: {
      upload: `${API_URL}/rag/diet/upload`,
      search: (query: string, k: number = 3) => `${API_URL}/rag/diet/search?query=${encodeURIComponent(query)}&k=${k}`,
      stats: `${API_URL}/rag/diet/stats`,
    },
    exercise: {
      upload: `${API_URL}/rag/exercise/upload`,
      search: (query: string, k: number = 3) => `${API_URL}/rag/exercise/search?query=${encodeURIComponent(query)}&k=${k}`,
      stats: `${API_URL}/rag/exercise/stats`,
    },
  },
  
  // Admin endpoints
  admin: {
    users: `${API_URL}/api/v1/admin/users`,
    health: `${API_URL}/api/v1/admin/health`,
    check: `${API_URL}/api/v1/admin/check`,
  },
  
  // Health check
  health: `${API_URL}/health`,
};

export default API_ENDPOINTS;

