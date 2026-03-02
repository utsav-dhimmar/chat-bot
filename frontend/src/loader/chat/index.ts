import { redirect, type LoaderFunctionArgs } from 'react-router-dom';
import { ChatServices } from '@/apis/services/chat.service';
import { z } from 'zod';
const RouterParamSchema = z.object({
  conversationId: z.uuid('v4'),
});

export async function chatLoader({ params }: LoaderFunctionArgs) {
  const conversation_Id = params;

  try {
    const { conversationId } = RouterParamSchema.parse(conversation_Id);
    const [session, messages] = await Promise.all([
      ChatServices.getSession(conversationId),
      ChatServices.getMessages(conversationId),
    ]);
    return { session, messages };
  } catch (e) {
    console.log(e);
    return redirect('/');
  }
}
