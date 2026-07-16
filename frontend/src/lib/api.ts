import axios from 'axios';

// Configure base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Bypass-Tunnel-Reminder': 'true',
  }
});

// Interceptor to attach auth token
apiClient.interceptors.request.use((config) => {
  // Use typeof window to check if we are on the client side
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Interceptor to handle 401 Unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
export interface AnalysisResponse {
  sample_id: string;
  patient_id: string;
  specimen_type: string;
  quality: string;
  prediction: string;
  confidence: number;
  uncertainty: number;
  infected_cells: number;
  total_cells: number;
  parasitemia: number;
  heatmap_path: string;
  report: string;
  review_required: boolean;
  model_versions: Record<string, string>;
}

export const analyzeImage = async (file: File, patientId: string, specimenType: string): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('patient_id', patientId);
  formData.append('specimen_type', specimenType);

  const response = await apiClient.post<AnalysisResponse>('/analyze/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getAnalysisHistory = async (skip = 0, limit = 100): Promise<AnalysisResponse[]> => {
  const response = await apiClient.get<AnalysisResponse[]>('/history', {
    params: { skip, limit },
  });
  return response.data;
};

export const getAnalysisById = async (sampleId: string): Promise<AnalysisResponse> => {
  const response = await apiClient.get<AnalysisResponse>(`/history/${sampleId}`);
  return response.data;
};
