import { adminAxiosClient } from '../adminClient';
import type {
  AdminLoginRequest,
  AdminLoginResponse,
  AdminMessageResponse,
  AdminQuestion,
  AdminStats,
  AdminUser,
  AdminUserDetail,
  DeleteUserResponse,
} from '../types/admin.types';

export const AdminServices = {
  login: async (credentials: AdminLoginRequest): Promise<AdminLoginResponse> => {
    const { data } = await adminAxiosClient.post<AdminLoginResponse>('/admin/login', credentials);
    return data;
  },

  getUsers: async (): Promise<AdminUser[]> => {
    const { data } = await adminAxiosClient.get<AdminUser[]>('/admin/users');
    return data;
  },

  getUserDetail: async (userId: string): Promise<AdminUserDetail> => {
    const { data } = await adminAxiosClient.get<AdminUserDetail>(`/admin/users/${userId}`);
    return data;
  },

  getQuestions: async (): Promise<AdminQuestion[]> => {
    const { data } = await adminAxiosClient.get<AdminQuestion[]>('/admin/questions');
    return data;
  },

  getStats: async (): Promise<AdminStats> => {
    const { data } = await adminAxiosClient.get<AdminStats>('/admin/stats');
    return data;
  },

  deactivateUser: async (userId: string): Promise<AdminMessageResponse> => {
    const { data } = await adminAxiosClient.put<AdminMessageResponse>(`/admin/users/${userId}/deactivate`);
    return data;
  },

  activateUser: async (userId: string): Promise<AdminMessageResponse> => {
    const { data } = await adminAxiosClient.put<AdminMessageResponse>(`/admin/users/${userId}/activate`);
    return data;
  },

  deleteUser: async (userId: string): Promise<DeleteUserResponse> => {
    const { data } = await adminAxiosClient.delete<DeleteUserResponse>(`/admin/users/${userId}`);
    return data;
  },

  makeAdmin: async (userId: string): Promise<AdminMessageResponse> => {
    const { data } = await adminAxiosClient.put<AdminMessageResponse>(`/admin/users/${userId}/make-admin`);
    return data;
  },
};
