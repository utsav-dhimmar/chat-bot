import { axiosClient } from '../client';
import type {
  AdminLoginRequest,
  AdminLoginResponse,
  PasswordChange,
  PasswordChangeResponse,
  TokenResponse,
  UserLogin,
  UserProfile,
  UserRegiser,
} from '../types/auth.types';

export const AuthServices = {
  register: async (data: UserRegiser): Promise<UserProfile> => {
    const { data: res } = await axiosClient.post<UserProfile>('/auth/register', data);
    return res;
  },
  login: async (data: UserLogin): Promise<TokenResponse> => {
    const { data: res } = await axiosClient.post<TokenResponse>('/auth/login', data);
    return res;
  },
  getMe: async (): Promise<UserProfile> => {
    const { data: res } = await axiosClient.get<UserProfile>('/auth/me');
    return res;
  },
  changePassword: async (data: PasswordChange): Promise<PasswordChangeResponse> => {
    const { data: res } = await axiosClient.post<PasswordChangeResponse>(
      '/auth/change-password',
      data
    );
    return res;
  },
  adminLogin: async (data: AdminLoginRequest): Promise<AdminLoginResponse> => {
    const { data: res } = await axiosClient.post<AdminLoginResponse>('/admin/login', data);
    return res;
  },
};
