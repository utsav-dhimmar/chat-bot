import axios from 'axios';
import { store } from '@/store';
import { setBan } from '@/store/slices/banSlice';

export const axiosClient = axios.create({
  baseURL: '/api',
});

// function run before api call
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token') || localStorage.getItem('adminToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = 'An unexpected error occurred';

    if (axios.isAxiosError(error)) {
      const data = error.response?.data;

      // FAST-API(Pydantic validation) style validation

      const detail = data?.detail;
      /*
      {
    "detail": [
        {
            "type": "value_error",
            "loc": [
                "body",
                "password"
            ],
            "msg": "Value error, Password must contain: at least one uppercase letter (A-Z), at least one lowercase letter (a-z)",
            "input": "123456789",
            "ctx": {
                "error": {}
            }
        }
    ]
      */
      const hasDeactivated =
        typeof detail === 'string' &&
        detail.toLowerCase().includes('account is deactivated');
      if (hasDeactivated) {
        store.dispatch(setBan(detail));
      }

      if (detail) {
        // detail must be res
        if (Array.isArray(detail)) {
          // should be array
          errorMessage = detail
            .map((err: any) => `${err.loc.slice(1).join('.')}: ${err.msg}`) // values after 0 index : message
            .join(', '); // join eniter thing
        } else {
          errorMessage = detail;
        }
      } else {
        errorMessage = data?.message || error.message || errorMessage;
      }
    } else if (error instanceof Error) {
      errorMessage = error.message;
    }

    return Promise.reject(new Error(errorMessage)); // throw it and hanlde at using api call
  }
);
