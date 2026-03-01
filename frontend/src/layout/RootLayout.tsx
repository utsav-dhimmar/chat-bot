import { Outlet } from 'react-router-dom';

export default function RootLayout() {
  return (
    <div className="vh-100 d-flex flex-column overflow-hidden">
      <main className="flex-grow-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
