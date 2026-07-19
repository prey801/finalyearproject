import axios from 'axios';
import { createClient } from '@/lib/supabase/client';

/**
 * API base URL resolution order:
 *  1. Runtime override stored in localStorage (set by Colab cell or DevTools)
 *  2. NEXT_PUBLIC_API_URL baked in at build time
 *  3. localhost fallback for local dev
 *
 * To update the backend URL without rebuilding (e.g. after ngrok restarts):
 *   localStorage.setItem('MEDSCOPE_API_URL', 'https://new-url.ngrok-free.app')
 *   location.reload()
 */
function resolveApiUrl(): string {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('MEDSCOPE_API_URL');
    if (stored) return stored;
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

const apiClient = axios.create({
  // baseURL is resolved lazily so runtime overrides take effect immediately
  baseURL: resolveApiUrl(),
  timeout: 30000,
  headers: {
    'Bypass-Tunnel-Reminder': 'true',
  },
});

// Re-resolve the URL on every request so localStorage changes take effect
// without needing a full page reload.
apiClient.interceptors.request.use(async (config) => {
  config.baseURL = resolveApiUrl();

  if (typeof window !== 'undefined') {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
  }
  return config;
});

// Redirect to /auth on 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      if (window.location.pathname !== '/auth') {
        window.location.href = '/auth';
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

export const analyzeImage = async (
  file: File,
  patientId: string,
  specimenType: string
): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('patient_id', patientId);
  formData.append('specimen_type', specimenType);

  const initialResponse = await apiClient.post<{
    task_id: string;
    sample_id: string;
    status: string;
  }>('/analyze/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  const { task_id: taskId, sample_id: sampleId } = initialResponse.data;

  return new Promise((resolve, reject) => {
    const pollInterval = setInterval(async () => {
      try {
        const statusResponse = await apiClient.get<{
          status: string;
          error?: string;
          sample_id?: string;
        }>(`/analyze/status/${taskId}`);

        if (statusResponse.data.status === 'completed') {
          clearInterval(pollInterval);
          clearTimeout(pollTimeout);
          resolve(await getAnalysisById(sampleId));
        } else if (statusResponse.data.status === 'failed') {
          clearInterval(pollInterval);
          clearTimeout(pollTimeout);
          reject(new Error(statusResponse.data.error || 'Analysis failed'));
        }
      } catch (error) {
        clearInterval(pollInterval);
        clearTimeout(pollTimeout);
        reject(error);
      }
    }, 2000);

    // Give up after 5 minutes
    const pollTimeout = setTimeout(() => {
      clearInterval(pollInterval);
      reject(new Error('Analysis timed out after 5 minutes. The server may be overloaded.'));
    }, 5 * 60 * 1000);
  });
};

export const getAnalysisHistory = async (
  skip = 0,
  limit = 100
): Promise<AnalysisResponse[]> => {
  const response = await apiClient.get<AnalysisResponse[]>('/history', {
    params: { skip, limit },
  });
  return response.data;
};

export const getAnalysisById = async (
  sampleId: string
): Promise<AnalysisResponse> => {
  const response = await apiClient.get<AnalysisResponse>(`/history/${sampleId}`);
  return response.data;
};

export const chatWithCopilot = async (
  message: string,
  context?: string
): Promise<string> => {
  const response = await apiClient.post<{ reply: string }>('/chat/', {
    message,
    context,
  });
  return response.data.reply;
};
