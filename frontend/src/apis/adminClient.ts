import axios from 'axios';

export const adminAxiosClient = axios.create({
  baseURL: '/api',
});

adminAxiosClient.interceptors.request.use(
  (config) => {
    const adminToken = localStorage.getItem('adminToken');
    if (adminToken) {
      config.headers.Authorization = `Bearer ${adminToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

adminAxiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = 'An unexpected error occurred';

    if (axios.isAxiosError(error)) {
      const data = error.response?.data;

      const detail = data?.detail;
      if (detail) {
        if (Array.isArray(detail)) {
          errorMessage = detail
            .map((err: unknown) => `${(err as { loc?: string[]; msg?: string }).loc?.slice(1).join('.')}: ${(err as { msg?: string }).msg}`)
            .join(', ');
        } else {
          errorMessage = detail;
        }
      } else {
        errorMessage = data?.message || error.message || errorMessage;
      }
    } else if (error instanceof Error) {
      errorMessage = error.message;
    }

    return Promise.reject(new Error(errorMessage));
  }
);
