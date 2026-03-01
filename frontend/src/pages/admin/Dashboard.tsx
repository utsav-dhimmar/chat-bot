import { QuestionList } from "@/components/admin/QuestionList";
import { UserList } from "@/components/admin/UserList";
import { DUMMY_QUESTIONS, DUMMY_USERS } from "@/temp/adminData";
import {
    RiDashboardLine,
    RiGroupLine,
    RiProhibitedLine,
    RiQuestionAnswerLine,
} from "@remixicon/react";
import { useState } from "react";

export default function AdminDashboard() {
	const [users, setUsers] = useState(DUMMY_USERS);
	const [questions, setQuestions] = useState(DUMMY_QUESTIONS);

	const handleBanUser = (id: string) => {
		setUsers(prev =>
			prev.map(u =>
				u.id === id
					? {
							...u,
							status: u.status === "active" ? "banned" : "active",
						}
					: u,
			),
		);
		setQuestions(prev => prev.filter(q => q.userId !== id));
	};

	const handleDeleteUser = (id: string) => {
		if (window.confirm("Are you sure you want to delete this user?")) {
			setUsers(prev => prev.filter(u => u.id !== id));
			setQuestions(prev => prev.filter(q => q.userId !== id));
		}
	};

	return (
		<div className="bg-light min-vh-100 p-4">
			<div className="container-fluid">
				{/* Header */}
				<div className="d-flex align-items-center mb-4 gap-2">
					<div className="bg-primary p-2 rounded text-white">
						<RiDashboardLine size={24} />
					</div>
					<div>
						<h3 className="mb-0 fw-bold">Admin Dashboard</h3>
					</div>
				</div>

				{/* Stats Row */}
				<div className="row g-4 mb-4">
					<div className="col-md-4">
						<div className="card border-0 shadow-sm p-3">
							<div className="d-flex align-items-center gap-3">
								<div className="bg-primary-subtle p-3 rounded-circle text-primary">
									<RiGroupLine size={24} />
								</div>
								<div>
									<div className="text-muted small">
										Total Users
									</div>
									<h4 className="mb-0 fw-bold">
										{users.length}
									</h4>
								</div>
							</div>
						</div>
					</div>
					<div className="col-md-4">
						<div className="card border-0 shadow-sm p-3">
							<div className="d-flex align-items-center gap-3">
								<div className="bg-info-subtle p-3 rounded-circle text-info">
									<RiQuestionAnswerLine size={24} />
								</div>
								<div>
									<div className="text-muted small">
										Total Questions
									</div>
									<h4 className="mb-0 fw-bold">
										{questions.length}
									</h4>
								</div>
							</div>
						</div>
					</div>
					<div className="col-md-4">
						<div className="card border-0 shadow-sm p-3">
							<div className="d-flex align-items-center gap-3">
								<div className="bg-danger-subtle p-3 rounded-circle text-danger">
									<RiProhibitedLine size={24} />
								</div>
								<div>
									<div className="text-muted small">
										Banned Users
									</div>
									<h4 className="mb-0 fw-bold">
										{
											users.filter(
												u => u.status === "banned",
											).length
										}
									</h4>
								</div>
							</div>
						</div>
					</div>
				</div>

				{/* Main Content */}
				<div className="row g-4">
					<div className="col-lg-7">
						<UserList
							users={users}
							onBan={handleBanUser}
							onDelete={handleDeleteUser}
						/>
					</div>
					<div className="col-lg-5">
						<QuestionList questions={questions} />
					</div>
				</div>
			</div>
		</div>
	);
}
