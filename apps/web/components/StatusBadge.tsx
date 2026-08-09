import type { UiState } from "./types";

const STATUS_LABELS: Record<UiState, string> = {
  loading: "Loading",
  fresh: "Fresh",
  stale: "Stale",
  deleted: "Deleted",
  pending_recheck: "Pending recheck",
  unavailable: "Unavailable",
  insufficient_context: "Insufficient context",
  refused: "Refused safely",
  failed: "Failed",
  no_accessible_context: "No accessible context",
  answered: "Answered",
  fixture: "Fixture",
  blocked: "Blocked",
  unverified: "Unverified",
};

const STATUS_MARKS: Record<UiState, string> = {
  loading: "…",
  fresh: "✓",
  stale: "!",
  deleted: "×",
  pending_recheck: "↻",
  unavailable: "—",
  insufficient_context: "?",
  refused: "×",
  failed: "×",
  no_accessible_context: "—",
  answered: "✓",
  fixture: "◆",
  blocked: "!",
  unverified: "?",
};

export function StatusBadge({ state, label }: { state: UiState; label?: string }) {
  return (
    <span className="status-badge" data-state={state} role="status">
      <span aria-hidden="true">{STATUS_MARKS[state]}</span>
      <span>{label ?? STATUS_LABELS[state]}</span>
    </span>
  );
}
