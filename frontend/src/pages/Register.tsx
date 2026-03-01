import { AuthServices } from '@/apis/services/auth.service';
import { Button, ErrorAlert, Input, ValidationCmp } from '@/components';
import { registerSchema, type RegisterFormData } from '@/schema/Auth';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';

export default function Register() {
  const navigate = useNavigate();
  const [backendError, setBackendError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setLoading(true);
      setBackendError(null);
      await AuthServices.register(data);
      navigate('/login');
    } catch (err: any) {
      if (err.details && Array.isArray(err.details)) {
        // [inputName: message...]
        const combinedError = err.details.map((errorDetail: any) => errorDetail.msg).join(', ');
        setBackendError(combinedError);
      } else {
        const msg = err.message || 'Something went wrong. Please try again.';
        setBackendError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100 bg-light">
      <div className="card shadow p-4" style={{ width: '400px' }}>
        <h2 className="text-center mb-4">Register</h2>
        <ErrorAlert message={backendError} />
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="mb-3">
            <Input
              lable="Username"
              type="text"
              className="form-control"
              error={!!errors.username}
              {...register('username')}
              autoComplete="username webauthn"
            />

            {errors.username && <ValidationCmp message={errors.username.message} />}
          </div>
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
              autoComplete="new-password webauthn"
            />

            {errors.password && <ValidationCmp message={errors.password.message} />}
          </div>
          <Button type="submit" className="btn-primary w-100" disabled={loading}>
            {loading ? 'Registering...' : 'Register'}
          </Button>
        </form>
        <p className="text-center mt-3">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
