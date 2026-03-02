import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

export function NotFound() {
  const navigate = useNavigate();

  useEffect(() => {
    const timerId = setTimeout(() => {
      navigate('/');
    }, 3 * 1000);
    () => clearTimeout(timerId);
  }, []);

  return (
    <div className="container vh-100 d-flex flex-column justify-content-center align-items-center text-center">
      <h1 className="display-1 fw-bold text-dark">404</h1>
      <h2 className="mb-4">oops! Page Not Found</h2>

      <div className="d-grid gap-2 d-sm-flex justify-content-sm-center">
        <button
          type="button"
          className="btn btn-primary btn-lg px-4 gap-3"
          onClick={() => navigate('/')}
        >
          Go to Home
        </button>
        <button
          type="button"
          className="btn btn-outline-secondary btn-lg px-4"
          onClick={() => navigate(-1)}
        >
          Go Back
        </button>
      </div>
    </div>
  );
}
