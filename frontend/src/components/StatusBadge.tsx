interface StatusBadgeProps {
  status: string
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = status.toLowerCase()

  return (
    <span className={`run-status ${normalized}`}>
      <span className="status-icon">
        {normalized === "success" && "✓"}
        {normalized === "failed" && "✗"}
        {normalized === "running" && "↻"}
        {normalized === "pending" && "⧗"}
        {normalized === "cancelled" && "⏹"}
      </span>
      <span className="status-text">
        {status}
      </span>
    </span>
  )
}