import { ChatHistory } from '@/components';
import { useState } from 'react';
import { Outlet } from 'react-router-dom';

export default function ChatLayout() {
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  return (
    <div className="container-fluid h-100 d-flex bg-light p-0 overflow-hidden">
      <ChatHistory isOpen={isHistoryOpen} onToggle={() => setIsHistoryOpen(!isHistoryOpen)} />
      <div className="flex-grow-1 h-100 overflow-hidden">
        <Outlet />
      </div>
    </div>
  );
}
