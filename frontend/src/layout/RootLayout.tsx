import { Outlet } from 'react-router-dom';
import { BannedModal } from '@/components';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { clearBan } from '@/store/slices/banSlice';

export default function RootLayout() {
  const dispatch = useAppDispatch();
  const banState = useAppSelector((state) => state.ban);

  const closeBanModal = () => {
    dispatch(clearBan());
  };

  return (
    <div className="vh-100 d-flex flex-column overflow-hidden">
      <BannedModal open={banState.isBanned} reason={banState.reason ?? undefined} onClose={closeBanModal} />
      <main className="flex-grow-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
