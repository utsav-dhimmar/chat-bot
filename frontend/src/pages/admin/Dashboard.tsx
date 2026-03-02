import { AdminServices } from "@/apis/services/admin.service";
import type { AdminQuestion, AdminUser } from "@/apis/types/admin.types";
import { QuestionList } from "@/components/admin/QuestionList";
import { UserList } from "@/components/admin/UserList";
import { logoutAdmin } from "@/store/slices/adminSlice";
import { RiDashboardLine, RiLogoutCircleLine } from "@remixicon/react";
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAppDispatch } from "@/store/hooks";

export default function AdminDashboard() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [questions, setQuestions] = useState<AdminQuestion[]>([]);

  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      console.log("Fetching data...");
      const usersData = await AdminServices.getUsers();
      console.log("Users:", usersData);
      const questionsData = await AdminServices.getQuestions();
      console.log("Questions:", questionsData);
      const statsData = await AdminServices.getStats();
      console.log("Stats:", statsData);
      // setUsers(usersData);
      setQuestions(questionsData);
    } catch (error) {
      console.error("Failed to fetch admin data:", error);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleBanUser = async (id: string) => {
    const user = users.find((u) => u.id === id);
    if (!user) return;

    try {
      if (user.is_active) {
        await AdminServices.deactivateUser(id);
      } else {
        await AdminServices.activateUser(id);
      }
      await fetchData();
    } catch (error) {
      console.error("Failed to update user status:", error);
    }
  };

  const handleDeleteUser = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this user?")) {
      try {
        await AdminServices.deleteUser(id);
        await fetchData();
      } catch (error) {
        console.error("Failed to delete user:", error);
      }
    }
  };

  const handleLogout = () => {
    dispatch(logoutAdmin());
    navigate("/admin/login");
  };

  const formatUsers = users.map((u) => ({
    id: u.id,
    name: u.username,
    email: u.email,
    status: u.is_active ? "active" : "banned",
    joinedAt: new Date(u.created_at).toLocaleDateString(),
  }));

  const formatQuestions = questions.map((q) => ({
    id: q.id,
    userId: q.user_id,
    userName: q.username || "Unknown",
    question: q.question,
    timestamp: new Date(q.created_at).toLocaleString(),
    documentTitle: "N/A",
  }));

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center vh-100">
        <div className="spinner-border text-primary">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-light min-vh-100 p-4">
      <div className="container-fluid">
        {/* Header */}
        <div className="d-flex align-items-center justify-content-between mb-4">
          <div className="d-flex align-items-center gap-2">
            <div className="bg-primary p-2 rounded text-white">
              <RiDashboardLine size={24} />
            </div>
            <div>
              <h3 className="mb-0 fw-bold">Admin Dashboard</h3>
            </div>
          </div>
          <button
            type="button"
            className="btn btn-outline-secondary d-flex align-items-center gap-2"
            onClick={handleLogout}
          >
            <RiLogoutCircleLine size={18} />
            Logout
          </button>
        </div>

        {/* Main Content */}
        <div className="row g-4">
          <div className="col-lg-7">
            <UserList
              users={formatUsers}
              onBan={handleBanUser}
              onDelete={handleDeleteUser}
            />
          </div>
          <div className="col-lg-5">
            <QuestionList questions={formatQuestions} />
          </div>
        </div>
      </div>
    </div>
  );
}
