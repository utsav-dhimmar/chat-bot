import {
  RiDeleteBin7Line,
  RiProhibitedLine,
  RiUserAddLine,
} from "@remixicon/react";

interface FormattedUser {
  id: string;
  name: string;
  email: string;
  status: "active" | "banned";
  joinedAt: string;
  documentCount: number;
  messageCount: number;
}

interface UserListProps {
  users: FormattedUser[];
  onBan: (id: string) => void;
  onDelete: (id: string) => void;
}

export function UserList({ users, onBan, onDelete }: UserListProps) {
  return (
    <div className="card shadow-sm border-0">
      <div className="card-header bg-white py-3">
        <h5 className="mb-0 fw-bold">User Management</h5>
      </div>
      <div className="card-body p-0">
        <div style={{ maxHeight: "600px", overflowY: "auto" }}>
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0 text-nowrap">
              <thead className="bg-light sticky-top">
                <tr>
                  <th className="px-4">User</th>
                  <th>Docs</th>
                  <th>Msgs</th>
                  <th>Joined</th>
                  <th>Status</th>
                  <th className="text-end px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-4">
                      <div className="d-flex align-items-center">
                        <div>
                          <div className="fw-semibold">{user.name}</div>
                          <div className="text-muted small">{user.email}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="badge bg-light text-dark border">
                        {user.documentCount}
                      </span>
                    </td>
                    <td>
                      <span className="badge bg-light text-dark border">
                        {user.messageCount}
                      </span>
                    </td>
                    <td className="text-muted small">{user.joinedAt}</td>
                    <td>
                      <span
                        className={`badge rounded-pill ${
                          user.status === "active"
                            ? "bg-success-subtle text-success"
                            : "bg-danger-subtle text-danger"
                        }`}
                      >
                        {user.status}
                      </span>
                    </td>
                    <td className="text-end px-4">
                      <div className="btn-group btn-group-sm">
                        <button
                          type="button"
                          className="btn btn-outline-warning"
                          onClick={() => onBan(user.id)}
                          title={
                            user.status === "active" ? "Ban User" : "Unban User"
                          }
                        >
                          {user.status === "active" && (
                            <RiProhibitedLine size={16} />
                          )}
                          {user.status === "banned" && (
                            <RiUserAddLine size={16} />
                          )}
                        </button>
                        <button
                          type="button"
                          className="btn btn-outline-danger"
                          onClick={() => onDelete(user.id)}
                          title="Delete User"
                        >
                          <RiDeleteBin7Line size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
