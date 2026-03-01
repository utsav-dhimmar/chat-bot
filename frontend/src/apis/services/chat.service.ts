import { axiosClient } from '../client';
import type { ChatAsk, ChatMessage, ChatResponse, ChatSession } from '../types/chat.types';

export const ChatServices = {
  ask: async (data: ChatAsk): Promise<ChatResponse> => {
    const { data: res } = await axiosClient.post<ChatResponse>('/chat/ask', data);
    return res;
  },
  listSessions: async (): Promise<ChatSession[]> => {
    const { data: res } = await axiosClient.get<ChatSession[]>('/chat/sessions');
    return res;
  },
  getMessages: async (sessionId: string): Promise<ChatMessage[]> => {
    const { data: res } = await axiosClient.get<ChatMessage[]>(
      `/chat/sessions/${sessionId}/messages`
    );
    return res;
  },
  deleteSession: async (sessionId: string): Promise<void> => {
    await axiosClient.delete(`/chat/sessions/${sessionId}`);
  },
};
