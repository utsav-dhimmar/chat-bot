export interface Document {
  document_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  page_count: number | null;
  chunk_count: number | null;
  status: 'processing' | 'ready' | 'error';
  created_at: string;
}

export interface DocumentUploadResponse {
  message: string;
  document_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  page_count: number | null;
  chunk_count: number | null;
  status: string;
}
