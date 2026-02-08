// API Configuration
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API Endpoints
export const API_ENDPOINTS = {
  upload: `${API_URL}/api/upload`,
  status: (jobId: string) => `${API_URL}/api/status/${jobId}`,
  download: (jobId: string) => `${API_URL}/api/download/${jobId}`,
  downloadSplat: (jobId: string) => `${API_URL}/api/download/${jobId}/splat`,
};
