import { AuthServices } from '@/apis/services/auth.service';
import { Button, ErrorAlert, Input, ValidationCmp } from '@/components';
import { loginSchema, type LoginFormData } from '@/schema/Auth';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm, type FieldErrors } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAppDispatch } from '@/store/hooks';
import { setCredentials } from '@/store/slices/authSlice';

export default function Login() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [backendError, setBackendError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      setLoading(true);
      setBackendError(null);
      const res = await AuthServices.login(data);
      console.log('Login success:', res);
      
      dispatch(setCredentials({
        user: res.user,
        token: res.access_token
      }));

      navigate('/');
    } catch (err: any) {
      if (err.details && Array.isArray(err.details)) {
        const combinedError = err.details.map((errorDetail: any) => errorDetail.msg).join(', ');
        setBackendError(combinedError);
      } else {
        const msg = err.message || 'Invalid email or password';
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
        <h2 className="text-center mb-4">Login</h2>
        <ErrorAlert message={backendError} />
        <form onSubmit={handleSubmit(onSubmit, logErrors)}>
          <div className="mb-3">
            <Input
              lable="Email"
              type="email"
              className="form-control"
              error={!!errors.email}
              {...register('email')}
              autoComplete="email webauthn"
            />

            {errors.email && <ValidationCmp message={errors.email.message} />}
          </div>
          <div className="mb-3">
            <Input
              lable="Password"
              type="password"
              className="form-control"
              error={!!errors.password}
              {...register('password')}
              autoComplete="current-password webauthn"
            />
            {errors.password && <ValidationCmp message={errors.password.message} />}
          </div>
          <Button type="submit" className="btn-primary w-100" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>
        <p className="text-center mt-3">
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}
