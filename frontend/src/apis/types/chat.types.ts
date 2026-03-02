export interface SourceChunk {
  chunk_id: string;
  content: string;
  similarity_score: number;
}

export interface ChatAsk {
  document_id: string;
  question: string;
  session_id?: string | null;
}

export interface ChatResponse {
  session_id: string;
  message_id: string;
  document_id: string;
  answer: string;
  sources: SourceChunk[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string | null;
  document_id: string;
  created_at: string;
  updated_at: string;
}
