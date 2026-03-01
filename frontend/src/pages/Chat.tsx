import { AIMessage, ChatHistory, HumanMessage } from '@/components/';
import { TEMP_CONVERSION } from '@/temp/data';
import { zodResolver } from '@hookform/resolvers/zod';
import { Fragment, useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useLoaderData } from 'react-router-dom';
import { z } from 'zod';

const MessageSchema = z.object({
  message: z.string().trim().min(5, {
    error: "Empty Message can't be send",
  }),
});
type messageData = z.infer<typeof MessageSchema>;

export default function Chat() {
  const { conversationId } = useLoaderData();

  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const {
    register,
    formState: { errors },
  } = useForm<messageData>({
    resolver: zodResolver(MessageSchema),
  });

  useEffect(() => {
    // TODO: GET TITLE FROM API THEN UPDATE IT
    document.title = 'THIS IS TITLE';
  }, []); // prefetch so no needed

  // TOD: hnalde validation and call api
  return (
    <div className="container-fluid h-100 d-flex bg-light p-0 overflow-hidden">
      <ChatHistory isOpen={isHistoryOpen} onToggle={() => setIsHistoryOpen(!isHistoryOpen)} />
      <div
        className="card shadow-sm flex-grow-1 h-100 border-0"
        style={{
          maxWidth: '100%',
          borderRadius: '0',
        }}
      >
        <div className="card-header bg-white py-3 border-bottom text-center">
          <h5 className="mb-0 fw-bold">
            {/* Title will display here */}
            Chat
          </h5>
        </div>
        <div className="card-body overflow-auto" style={{ flex: 1 }}>
          {TEMP_CONVERSION.map(({ role, text }) => (
            <Fragment key={text}>
              {role === 'HUMAN' && <HumanMessage message={text} />}
              {role === 'AI' && <AIMessage message={text} />}
            </Fragment>
          ))}
        </div>
        <div className="card-footer">
          <form className="d-flex align-items-center gap-2">
            <div className="flex-grow-1">
              <input
                type="text"
                className={`form-control ${errors.message ? 'is-invalid' : ''}`}
                placeholder="Type message..."
                {...register('message')}
              />
              {errors.message && <div className="invalid-feedback">{errors.message.message}</div>}
            </div>
            <button type="button" className="btn btn-primary">
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
