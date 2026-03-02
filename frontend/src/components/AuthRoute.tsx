import { useAppSelector } from '@/store/hooks';
import { Navigate, Outlet } from 'react-router-dom';

// For Only loggedin user
export function ProtectedRoute() {
  const { isAuthenticated } = useAppSelector((state) => state.auth);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

// Anyone can access
// user is already loggedin then it can't access login and register
export function PublicRoute() {
  const { isAuthenticated } = useAppSelector((state) => state.auth);

  if (isAuthenticated) {
    return <Navigate to="/new" replace />;
  }

  return <Outlet />;
}

// For Only loggedin admin
export function AdminProtectedRoute() {
  const { isAuthenticated } = useAppSelector((state) => state.admin);

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }

  return <Outlet />;
}
