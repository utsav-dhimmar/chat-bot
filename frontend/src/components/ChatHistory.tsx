import { RiChatNewFill, RiCloseFill, RiMenu2Line } from '@remixicon/react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from './Button';
const TESTING_DATA = Array.from({ length: 10 }).map((_, index) => ({
  id: crypto.randomUUID(),
  title: `this is title ${index + 1}`,
}));

export function ChatHistory({ isOpen, onToggle }: { isOpen: boolean; onToggle: () => void }) {
  const navigate = useNavigate();
  return (
    <aside
      className="h-100 overflow-hidden p-2 bg-white border-end shadow-sm d-flex flex-column"
      style={{
        width: isOpen ? '280px' : '60px',
        flexShrink: 0,
        transition: 'width 0.2s ease-in-out',
      }}
    >
      <div className="d-flex flex-column gap-2">
        <button
          type="button"
          className="btn btn-outline-secondary btn-sm w-100"
          onClick={onToggle}
          title={isOpen ? 'Close History' : 'Open History'}
        >
          {isOpen ? <RiCloseFill /> : <RiMenu2Line />}
        </button>
        {isOpen && (
          <Button type="button" className="btn-info btn-sm w-100" onClick={(_) => navigate('/new')}>
            New Chat <RiChatNewFill />
          </Button>
        )}
      </div>
      {isOpen && (
        <ul className="list-group mt-3 overflow-auto flex-grow-1">
          {TESTING_DATA.map(({ id, title }) => (
            <li className="list-group-item list-group-item-action text-center p-2" key={id}>
              <Link
                to={{
                  pathname: `/chat/${id}`,
                }}
                className="text-decoration-none text-dark small d-block text-truncate"
              >
                {title}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
