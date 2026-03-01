import ChatLayout from "@/layout/ChatLayout";
import RootLayout from "@/layout/RootLayout";
import { chatLoader } from "@/loader/chat";
import Chat from "@/pages/Chat";
import Login from "@/pages/Login";
import NewPdf from "@/pages/NewPdf";
import Register from "@/pages/Register";
import AdminDashboard from "@/pages/admin/Dashboard";
import { createBrowserRouter, Navigate } from "react-router-dom";
import { NotFound } from "@/components/NotFound";
import { ProtectedRoute, PublicRoute } from "@/components";

export const browserRoutes = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/new" replace />,
      },
      {
        element: <PublicRoute />,
        children: [
          {
            path: "login",
            element: <Login />,
          },
          {
            path: "register",
            element: <Register />,
          },
        ],
      },
      {
        element: <ProtectedRoute />,
        children: [
          {
            path: "admin",
            element: <AdminDashboard />,
          },
          {
            element: <ChatLayout />,
            children: [
              {
                path: "chat/:conversationId",
                element: <Chat />,
                loader: chatLoader,
              },
              {
                path: "new",
                element: <NewPdf />,
              },
            ],
          },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <NotFound />,
  },
]);
