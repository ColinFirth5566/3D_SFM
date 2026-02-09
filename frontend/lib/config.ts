// API Configuration
// Priority: localStorage override > build-time env > localhost default
function getApiUrl(): string {
  if (typeof window !== 'undefined') {
    const override = localStorage.getItem('NEXT_PUBLIC_API_URL');
    if (override) return override.replace(/\/+$/, '');
  }
  return (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
}

export const API_URL = getApiUrl();

// API Endpoints
export const API_ENDPOINTS = {
  upload: `${API_URL}/api/upload`,
  status: (jobId: string) => `${API_URL}/api/status/${jobId}`,
  download: (jobId: string) => `${API_URL}/api/download/${jobId}`,
  downloadSplat: (jobId: string) => `${API_URL}/api/download/${jobId}/splat`,
  downloadPly: (jobId: string) => `${API_URL}/api/download/${jobId}/ply`,
};
