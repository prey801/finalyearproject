import axios from 'axios';
import { createClient } from '@/lib/supabase/client';

// Configure base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    // Skip ngrok's browser-warning interstitial (returned as HTML on the
    // free plan for any request without this header — breaks JSON parsing).
    'ngrok-skip-browser-warning': 'true',
  }
});

// Interceptor to attach auth token — reads from active Supabase session
apiClient.interceptors.request.use(async (config) => {
  if (typeof window !== 'undefined') {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
  }
  return config;
});

// Interceptor to handle 401 Unauthorized — redirect to /auth (not /login)
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
export interface Detection {
  class_name: string;
  bbox: number[]; // [x, y, width, height] in original image pixel coordinates
  confidence: number;
}

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
  detections: Detection[];
  heatmap_path: string;
  report: string;
  review_required: boolean;
  model_versions: Record<string, string>;
  image_path: string | null;
  image_typicality: number | null;
}

export interface SimilarCase {
  sample_id: string;
  patient_id: string;
  prediction: string;
  parasitemia: number;
  similarity: number;
}

export const getSimilarCases = async (sampleId: string, limit = 5): Promise<SimilarCase[]> => {
  const response = await apiClient.get<SimilarCase[]>(`/history/${sampleId}/similar`, {
    params: { limit },
  });
  return response.data;
};

export const analyzeImage = async (file: File, patientId: string, specimenType: string): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('patient_id', patientId);
  formData.append('specimen_type', specimenType);

  // Initial request to trigger Celery task
  const initialResponse = await apiClient.post<{ task_id: string, sample_id: string, status: string }>('/analyze/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  const taskId = initialResponse.data.task_id;
  const sampleId = initialResponse.data.sample_id;

  // Poll for completion
  return new Promise((resolve, reject) => {
    const pollInterval = setInterval(async () => {
      try {
        const statusResponse = await apiClient.get<{ status: string, error?: string, sample_id?: string }>(`/analyze/status/${taskId}`);
        if (statusResponse.data.status === 'completed') {
          clearInterval(pollInterval);
          clearTimeout(pollTimeout);
          // Fetch final result
          const result = await getAnalysisById(sampleId);
          resolve(result);
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
    }, 2000); // poll every 2 seconds

    // Safety valve: give up after 5 minutes so the UI never hangs permanently
    const pollTimeout = setTimeout(() => {
      clearInterval(pollInterval);
      reject(new Error('Analysis timed out after 5 minutes. The server may be overloaded.'));
    }, 5 * 60 * 1000);
  });
};

export const getAnalysisHistory = async (skip = 0, limit = 100): Promise<AnalysisResponse[]> => {
  const response = await apiClient.get<AnalysisResponse[]>('/history', {
    params: { skip, limit },
  });
  return response.data;
};

export interface MetricsSummary {
  images_analyzed: number;
  images_analyzed_change_pct: number | null;
  flagged_abnormalities: number;
  flagged_rate_pct: number;
  avg_processing_time_s: number | null;
  avg_processing_time_change_s: number | null;
}

export const getMetricsSummary = async (range: string): Promise<MetricsSummary> => {
  const response = await apiClient.get<MetricsSummary>('/history/summary', {
    params: { range },
  });
  return response.data;
};

export const getAnalysisById = async (sampleId: string): Promise<AnalysisResponse> => {
  const response = await apiClient.get<AnalysisResponse>(`/history/${sampleId}`);
  return response.data;
};

// A plain <img src="..."> pointed straight at a backend-served path (e.g.
// image_path from a past case) can't set custom headers, so on ngrok's free
// plan it hits the browser-warning interstitial instead of the real image
// (the ngrok-skip-browser-warning header apiClient sends never gets sent by
// the <img> tag itself). Fetch it through apiClient instead and hand back an
// object URL. Caller is responsible for URL.revokeObjectURL when done.
export const fetchImageAsBlobUrl = async (path: string): Promise<string> => {
  const response = await apiClient.get(path, { responseType: 'blob' });
  return URL.createObjectURL(response.data);
};

export const chatWithCopilot = async (message: string, context?: string): Promise<string> => {
  // Unlike /analyze/ (fire-and-poll), this is a single synchronous round trip
  // through auth session lookup + ngrok tunnel + LLM completion — the global
  // 10s timeout is too tight for that chain and was aborting client-side
  // while the backend was still working (and would return successfully).
  const response = await apiClient.post<{ reply: string }>('/chat/', { message, context }, { timeout: 45000 });
  return response.data.reply;
};
