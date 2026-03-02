import { ChatServices } from '@/apis/services/chat.service';
import type { ChatMessage, ChatSession } from '@/apis/types';
import { AIMessage, HumanMessage } from '@/components/';
import { zodResolver } from '@hookform/resolvers/zod';
import { Fragment, useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useLoaderData, useParams, useSearchParams } from 'react-router-dom';
import { z } from 'zod';

const MessageSchema = z.object({
  message: z.string().trim().min(5, {
    error: "Empty Message can't be send",
  }),
});
type messageData = z.infer<typeof MessageSchema>;

interface LoaderData {
  session: ChatSession;
  messages: ChatMessage[];
}

export default function Chat() {
  const { conversationId } = useParams<{ conversationId: string }>();
  const [searchParams] = useSearchParams();
  const loaderData = useLoaderData<LoaderData>();
  const document_id = loaderData?.session?.document_id || searchParams.get('document_id') || ''; // helper for once when PDF is uploaded
  const [messages, setMessages] = useState<{ role: string; content: string; id?: string }[]>([]);

  const [loading, setLoading] = useState(false);
  const {
    register,
    formState: { errors },
    handleSubmit,
    reset,
  } = useForm<messageData>({
    resolver: zodResolver(MessageSchema),
  });

  useEffect(() => {
    if (loaderData?.messages) {
      setMessages(
        loaderData.messages.map((m) => ({
          role: m.role,
          content: m.content,
          id: m.id,
        }))
      );
    }
  }, [loaderData.messages]);

  const onSubmit = async (formData: messageData) => {
    if (!conversationId || !document_id) return;
    try {
      const response = await ChatServices.ask({
        session_id: conversationId,
        document_id,
        question: formData.message,
      });
      setMessages((prev) => [
        ...prev,
        { role: 'user', content: formData.message },
        { role: 'assistant', content: response.answer },
      ]);
      reset();
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };
  return (
    <div
      className="card shadow-sm flex-grow-1 h-100 border-0"
      style={{
        maxWidth: '100%',
        borderRadius: '0',
      }}
    >
      <div className="card-header bg-white py-3 border-bottom text-center">
        <h5 className="mb-0 fw-bold">{loaderData.session.title}</h5>
      </div>
      <div className="card-body overflow-auto" style={{ flex: 1 }}>
        {loading ? (
          <div className="text-center py-4">Loading...</div>
        ) : messages?.length === 0 ? (
          <div className="text-center py-4 text-muted">No messages yet</div>
        ) : (
          messages?.map(({ content, id, role }, index) => (
            <Fragment key={id || index}>
              {role === 'user' && <HumanMessage message={content} />}
              {role === 'assistant' && <AIMessage message={content} />}
            </Fragment>
          ))
        )}
      </div>
      <div className="card-footer">
        <form className="d-flex align-items-center gap-2" onSubmit={handleSubmit(onSubmit)}>
          <div className="flex-grow-1">
            <input
              type="text"
              className={`form-control ${errors.message ? 'is-invalid' : ''}`}
              placeholder="Type message..."
              {...register('message')}
            />
            {errors.message && <div className="invalid-feedback">{errors.message.message}</div>}
          </div>
          <button type="submit" className="btn btn-primary">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
