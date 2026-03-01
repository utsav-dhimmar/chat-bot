import { redirect, type LoaderFunctionArgs } from 'react-router-dom';
import { z } from 'zod';
const RouterParamSchema = z.object({
  conversationId: z.uuid(),
});

export async function chatLoader({ params }: LoaderFunctionArgs) {
  const conversation_Id = params;

  try {
    const { conversationId } = RouterParamSchema.parse(conversation_Id);
    return { conversationId };
  } catch (e) {
    console.log(e);
    // TODO: login appropriate place
    return redirect('/login');
  }
}
