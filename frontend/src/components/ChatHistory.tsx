import {
  RiChatNewFill,
  RiCloseFill,
  RiLogoutBoxLine,
  RiMenu2Line,
  RiUserLine,
} from "@remixicon/react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "./Button";
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { logout } from "@/store/slices/authSlice";
import { ChatServices } from "@/apis/services/chat.service";
import { useState, useEffect } from "react";
import type { ChatSession } from "@/apis/types";

export function ChatHistory({
  isOpen,
  onToggle,
}: {
  isOpen: boolean;
  onToggle: () => void;
}) {
  const [session, setSession] = useState<null | ChatSession[]>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const f = async () => {
      setLoading(true);
      try {
        const d = await ChatServices.listSessions();
        setSession(d || []);
      } catch (error) {
        setSession([]);
      } finally {
        setLoading(false);
      }
    };
    f();
  }, []);

  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login");
  };

  return (
    <aside
      className="h-100 overflow-hidden p-2 bg-white border-end shadow-sm d-flex flex-column"
      style={{
        width: isOpen ? "280px" : "60px",
        flexShrink: 0,
        transition: "width 0.2s ease-in-out",
      }}
    >
      <div className="d-flex flex-column gap-2">
        <button
          type="button"
          className="btn btn-outline-secondary btn-sm w-100"
          onClick={onToggle}
          title={isOpen ? "Close History" : "Open History"}
        >
          {isOpen ? <RiCloseFill /> : <RiMenu2Line />}
        </button>
        {isOpen && (
          <Button
            type="button"
            className="btn-info btn-sm w-100"
            onClick={(_) => navigate("/new")}
          >
            New Chat <RiChatNewFill />
          </Button>
        )}
      </div>
      {isOpen && (
        <ul className="list-group mt-3 overflow-auto flex-grow-1">
          {session && session.length > 0 ? (
            session.map(({ id, title }) => (
              <li
                className="list-group-item list-group-item-action text-center p-2"
                key={id}
              >
                <Link
                  to={{
                    pathname: `/chat/${id}`,
                  }}
                  className="text-decoration-none text-dark small d-block text-truncate"
                >
                  {title}
                </Link>
              </li>
            ))
          ) : (
            !loading && (
              <li className="list-group-item text-center p-3 text-muted border-0">
                <small>No chat found</small>
              </li>
            )
          )}
        </ul>
      )}

      <div className="mt-auto pt-3 border-top">
        {isOpen ? (
          <div className="d-flex flex-column gap-2">
            <div className="d-flex align-items-center gap-2 px-2 py-1 bg-light rounded text-truncate">
              <RiUserLine size={20} className="text-secondary" />
              <span className="small fw-medium text-dark">
                {user?.username || "User"}
              </span>
            </div>
            <button
              type="button"
              className="btn btn-outline-danger btn-sm d-flex align-items-center justify-content-center gap-2"
              onClick={handleLogout}
            >
              <RiLogoutBoxLine size={18} /> Logout
            </button>
          </div>
        ) : (
          <div className="d-flex flex-column align-items-center gap-2">
            <RiUserLine size={24} className="text-secondary" />
            <button
              type="button"
              className="btn btn-link text-danger p-0"
              onClick={handleLogout}
              title="Logout"
            >
              <RiLogoutBoxLine size={24} />
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
