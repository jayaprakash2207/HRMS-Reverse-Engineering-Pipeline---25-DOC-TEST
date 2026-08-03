import axios from 'axios';

// Mirrors backend's ErrorResponse (Stack Mapping Contract row 10 / GlobalExceptionHandler):
// { timestamp, status, errorCode, message, path, traceId }.
export interface ApiErrorResponse {
  timestamp: string;
  status: number;
  errorCode: string;
  message: string;
  path: string;
  traceId: string;
}

export function extractApiError(error: unknown): ApiErrorResponse | null {
  if (axios.isAxiosError(error) && error.response?.data) {
    return error.response.data as ApiErrorResponse;
  }
  return null;
}

export function getHttpStatus(error: unknown): number | null {
  if (axios.isAxiosError(error) && typeof error.response?.status === 'number') {
    return error.response.status;
  }
  return null;
}
