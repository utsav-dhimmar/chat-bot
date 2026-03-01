export interface AdminUser {
  id: string;
  name: string;
  email: string;
  status: "active" | "banned";
  joinedAt: string;
}

export interface UserQuestion {
  id: string;
  userId: string;
  userName: string;
  question: string;
  timestamp: string;
  documentTitle: string;
}

export const DUMMY_USERS: AdminUser[] = [
  {
    id: "1",
    name: "John Doe",
    email: "john@example.com",
    status: "active",
    joinedAt: "2024-01-15",
  },
  {
    id: "2",
    name: "Jane Smith",
    email: "jane@example.com",
    status: "active",
    joinedAt: "2024-02-10",
  },
  {
    id: "3",
    name: "Bob Wilson",
    email: "bob@example.com",
    status: "banned",
    joinedAt: "2023-11-05",
  },
];

export const DUMMY_QUESTIONS: UserQuestion[] = [
  {
    id: "q1",
    userId: "1",
    userName: "John Doe",
    question: "how to login ?",
    timestamp: "2024-03-01 10:30",
    documentTitle: "User Guide.pdf",
  },
  {
    id: "q2",
    userId: "2",
    userName: "Jane Smith",
    question: "what is refund policy",
    timestamp: "2024-03-01 11:15",
    documentTitle: "FAQ.pdf",
  },
  {
    id: "q3",
    userId: "1",
    userName: "John Doe",
    question: "summries the pdf",
    timestamp: "2024-03-01 12:00",
    documentTitle: "Features.pdf",
  },
];
