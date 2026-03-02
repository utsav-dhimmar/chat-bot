export interface AdminLoginRequest {
  email: string;
  password: string;
}

export interface AdminLoginResponse {
  access_token: string;
  token_type: string;
  admin_email: string;
}

export interface AdminUser {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  document_count: number;
  message_count: number;
  created_at: string;
}

export interface AdminUserDocument {
  document_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  status: string;
  created_at: string;
}

export interface AdminUserDetail {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  documents: AdminUserDocument[];
}

export interface AdminQuestion {
  id: string;
  question: string;
  user_id: string;
  username: string | null;
  email: string | null;
  session_id: string;
  created_at: string;
}

export interface AdminStats {
  users: {
    total: number;
    active: number;
    inactive: number;
  };
  documents: {
    total: number;
    ready: number;
    disk_mb: number;
  };
  chunks: number;
  sessions: number;
  messages: number;
}

export interface AdminMessageResponse {
  message: string;
}

export interface DeleteUserResponse {
  message: string;
  deleted_files: number;
  deleted_docs: number;
}
