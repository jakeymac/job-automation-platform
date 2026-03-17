import { useEffect, useState } from "react"
import { useParams } from "react-router"
import { apiFetch } from "../api/client"

interface JobRun {
  id: number
  job_id: number
  status: string
  exit_code: number | null
  triggered_by: string
  trigger_type: string
  created_at: string
  started_at: string | null
  finished_at: string | null
  duration_seconds: number | null
  log: string
}

export default function ViewJobRun() {
  const { id } = useParams()
  const [run, setRun] = useState<JobRun | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchRun() {
      try {
        const response = await apiFetch(`http://127.0.0.1:8000/api/jobs/runs/${id}/`)
        if (!response.ok) {
            throw new Error("Failed to load job run details")
        }
        const data = await response.json()
        setRun(data)
      } catch (error) {
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    fetchRun()
  }, [id])

  if (loading) {
    return <div className="job-run-page">Loading run details...</div>
  }
  if (!run) return <div className="job-run-page">Run not found</div>

  return (
    <div className="job-run-page">
      <div className="job-run-card">
        <h1>Job Run #{run.id}</h1>

        <div className="job-run-details">
          <div><strong>Status:</strong> {run.status}</div>
          <div><strong>Created:</strong> {run.created_at}</div>
          <div><strong>Started:</strong> {run.started_at || "-"}</div>
          <div><strong>Finished:</strong> {run.finished_at || "-"}</div>
          <div><strong>Exit Code:</strong> {run.exit_code ?? "-"}</div>
          <div><strong>Duration:</strong> {run.duration_seconds !== null ? `${run.duration_seconds} seconds` : "-"}</div>
          <div><strong>Triggered By:</strong> {run.triggered_by}</div>
          <div><strong>Trigger Type:</strong> {run.trigger_type}</div>
        </div>

        <h2>Logs</h2>
        <pre className="job-run-logs">
          {run.log || "No logs available"}
        </pre>
      </div>
    </div>
  )
}