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
