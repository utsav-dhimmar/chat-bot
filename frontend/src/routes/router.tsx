import ChatLayout from '@/layout/ChatLayout';
import RootLayout from '@/layout/RootLayout';
import { chatLoader } from '@/loader/chat';
import Chat from '@/pages/Chat';
import Login from '@/pages/Login';
import NewPdf from '@/pages/NewPdf';
import Register from '@/pages/Register';
import AdminDashboard from '@/pages/admin/Dashboard';
import { createBrowserRouter } from 'react-router-dom';

export const browserRoutes = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <Login />,
      },
      {
        path: 'login',
        element: <Login />,
      },
      {
        path: 'register',
        element: <Register />,
      },
      {
        path: 'admin',
        element: <AdminDashboard />,
      },
      {
        element: <ChatLayout />,
        children: [
          {
            path: 'chat/:conversationId',
            element: <Chat />,
            loader: chatLoader,
          },
          {
            path: 'new',
            element: <NewPdf />,
          },
        ],
      },
    ],
  },
]);
