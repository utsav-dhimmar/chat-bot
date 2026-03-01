import { axiosClient } from '../client';
import type { Document, DocumentUploadResponse } from '../types/document.types';

export const DocumentServices = {
  upload: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const { data: res } = await axiosClient.post<DocumentUploadResponse>(
      '/documents/upload',
      formData
    );
    return res;
  },
  list: async (): Promise<Document[]> => {
    const { data: res } = await axiosClient.get<Document[]>('/documents/');
    return res;
  },
  delete: async (documentId: string): Promise<void> => {
    await axiosClient.delete(`/documents/${documentId}`);
  },
};
