import type { UserQuestion } from "@/temp/adminData";
import { RiCalendarLine, RiFileTextLine } from "@remixicon/react";

interface QuestionListProps {
  questions: UserQuestion[];
}

export function QuestionList({ questions }: QuestionListProps) {
  return (
    <div className="card shadow-sm border-0 h-100">
      <div className="card-header bg-white py-3">
        <h5 className="mb-0 fw-bold">Recent User Questions</h5>
      </div>
      <div className="card-body overflow-auto p-0">
        <ul className="list-group list-group-flush">
          {questions.map((q) => (
            <li className="list-group-item p-4 border-bottom" key={q.id}>
              <div className="d-flex justify-content-between align-items-start mb-2">
                <div className="d-flex align-items-center">
                  <div className="fw-bold me-2">{q.userName}</div>
                  <span className="badge bg-secondary-subtle text-secondary small px-2 py-1 rounded-pill">
                    <RiFileTextLine size={12} className="me-1" />
                    {q.documentTitle}
                  </span>
                </div>
                <div className="text-muted small d-flex align-items-center">
                  <RiCalendarLine size={14} className="me-1" />
                  {q.timestamp}
                </div>
              </div>
              <p className="text-dark mb-0 bg-light p-3 rounded border-start border-primary border-4">
                {q.question}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
