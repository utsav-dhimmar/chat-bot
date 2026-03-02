import type { MouseEventHandler } from "react";

interface BannedModalProps {
  open: boolean;
  reason?: string;
  onClose: MouseEventHandler<HTMLButtonElement>;
}

export function BannedModal({ open, reason, onClose }: BannedModalProps) {
  if (!open) return null;

  return (
    <div
      aria-live="assertive"
      role="alertdialog"
      className="position-fixed top-0 start-0 vw-100 vh-100 d-flex align-items-center justify-content-center"
      style={{ backgroundColor: "rgba(0, 0, 0, 0.6)", zIndex: 1050 }}
    >
      <div
        className="card shadow-lg border-0 mx-3"
        style={{ maxWidth: "420px" }}
      >
        <div className="card-body text-center">
          <h5 className="card-title mb-3 fw-bold">Account Suspended</h5>
          <p className="mb-2">You are banned.</p>
          {reason && <p className="text-muted small mb-4">Reason: {reason}</p>}
          <button
            type="button"
            className="btn btn-danger w-100"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
