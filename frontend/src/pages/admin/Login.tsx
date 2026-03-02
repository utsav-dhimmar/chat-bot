import { AuthServices } from '@/apis/services/auth.service';
import { Button, ErrorAlert, Input, ValidationCmp } from '@/components';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm, type FieldErrors } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAppDispatch } from '@/store/hooks';
import { setAdminCredentials } from '@/store/slices/adminSlice';
import { z } from 'zod';

const adminLoginSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, 'Email is required')
    .email('Invalid email address'),
  password: z
    .string()
    .trim()
    .min(1, 'Password is required'),
});

type AdminLoginFormData = z.infer<typeof adminLoginSchema>;

export default function AdminLogin() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [backendError, setBackendError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AdminLoginFormData>({
    resolver: zodResolver(adminLoginSchema),
  });

  const onSubmit = async (data: AdminLoginFormData) => {
    try {
      setLoading(true);
      setBackendError(null);
      const res = await AuthServices.adminLogin(data);

      dispatch(
        setAdminCredentials({
          token: res.access_token,
          email: res.admin_email,
        })
      );

      navigate('/admin');
    } catch (err: any) {
      if (err.details && Array.isArray(err.details)) {
        const combinedError = err.details.map((errorDetail: any) => errorDetail.msg).join(', ');
        setBackendError(combinedError);
      } else {
        const msg = err.message || 'Invalid admin credentials';
        setBackendError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const logErrors = (d: FieldErrors<{ email: string; password: string }>) => {
    console.log(d);
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100 bg-light">
      <div className="card shadow p-4" style={{ width: '400px' }}>
        <div className="text-center mb-4">
          <div className="bg-primary rounded-circle d-inline-flex justify-content-center align-items-center mb-3" style={{ width: '60px', height: '60px' }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="white" viewBox="0 0 16 16" aria-hidden="true">
              <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6m2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0m4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4m-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10s-3.516.68-4.168 1.332c-.678.678-.83 1.418-.832 1.664z"/>
            </svg>
          </div>
          <h4 className="fw-bold">Admin Login</h4>
          <p className="text-muted small mb-0">Enter admin credentials</p>
        </div>
        
        <ErrorAlert message={backendError} />
        <form onSubmit={handleSubmit(onSubmit, logErrors)}>
          <div className="mb-3">
            <Input
              lable="Email"
              type="email"
              className="form-control"
              error={!!errors.email}
              {...register('email')}
              autoComplete="email"
            />
            {errors.email && <ValidationCmp message={errors.email.message} />}
          </div>
          <div className="mb-4">
            <Input
              lable="Password"
              type="password"
              className="form-control"
              error={!!errors.password}
              {...register('password')}
              autoComplete="current-password"
            />
            {errors.password && <ValidationCmp message={errors.password.message} />}
          </div>
          <Button type="submit" className="btn-primary w-100 py-2" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>
        <div className="text-center mt-3">
          <Link to="/login" className="text-decoration-none small">
            Back to User Login
          </Link>
        </div>
      </div>
    </div>
  );
}
