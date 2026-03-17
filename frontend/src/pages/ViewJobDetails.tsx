import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { apiFetch } from "../api/client"
import { readableSchedule } from "../utils/cron"


interface Job {
  id: number
  name: string
  description: string
  schedule: string
  is_active: boolean
  command: string
  image: string
}

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

export default function ViewJobDetails() {
  const { id } = useParams()
  const [job, setJob] = useState<Job | null>(null)
  const [ files, setFiles] = useState<any[]>([])
  const [jobRuns, setJobRuns] = useState<JobRun[]>([])
  const [loadingJobDetails, setLoadingJobDetails] = useState(true)
  const [loadingJobRuns, setLoadingJobRuns] = useState(true)

  const navigate = useNavigate()

  async function runJob() {
    try {
      const response = await apiFetch(`http://127.0.0.1:8000/api/jobs/${id}/run/`,
        {
          method: "POST"
        }
      )
      if (!response.ok) {
        throw new Error("Failed to run job")
      }
      const data = await response.json()
      console.log("Job run successfully:", data)
    } catch (error) {
      console.error("Failed to run job:", error)
    }
  }

  useEffect(() => {
    async function loadJob() {
      try {
        const jobDetailsResponse = await apiFetch(`http://127.0.0.1:8000/api/jobs/${id}/`,)
        if (!jobDetailsResponse.ok) {
          throw new Error("Failed to load job")
        }
        const jobDetailsData = await jobDetailsResponse.json()
        
        setJob(jobDetailsData)
      } catch {
        console.error("Failed to load job")
      } finally {
        setLoadingJobDetails(false)
      }
    }


    async function loadFiles() {
      try {
        const response = await apiFetch(`http://127.0.0.1:8000/api/jobs/${id}/files/`)
        if (!response.ok) {
          throw new Error("Failed to load files")
        }
        const data = await response.json()
        setFiles(data)
      } catch {
        console.error("Failed to load files")
      }
    }

    async function loadJobRuns() {
      try {
        const jobRunsResponse = await apiFetch(`http://127.0.0.1:8000/api/jobs/${id}/runs/`,)
        if (!jobRunsResponse.ok) {
          throw new Error("Failed to load job runs")
        }
        const jobRunsData = await jobRunsResponse.json()
        setJobRuns(jobRunsData)
        console.log("Job runs:", jobRunsData)
      } catch {
        console.error("Failed to load job runs")
      } finally {
        setLoadingJobRuns(false)
      }
    }

    loadJob()
    loadFiles()
    loadJobRuns()
  }, [id])

  if (loadingJobDetails) {
    return <div className="job-details-page">LoadingJobDetails job...</div>
  }

  if (!job) {
    return <div className="job-details-page">Job not found</div>
  }

  return (
  <div className="job-details-page">
    <div className="job-details-card">

      <div className="job-header">
        <div className="job-title-group">
          <h1 className="job-title">{job.name}</h1>

          <span className={`job-status-badge ${job.is_active ? "active" : "inactive"}`}>
            {job.is_active ? "Active" : "Inactive"}
          </span>
        </div>

        <div className="job-actions">
          <button
            className="job-edit-btn"
            onClick={() => navigate(`/jobs/${job.id}/edit`)}
          >
            Edit
          </button>

          <button className="job-run-btn" onClick={runJob}>
            Run
          </button>
        </div>
      </div>

      <div className="job-detail-row">
        <strong>Description:</strong>
        <span>{job.description}</span>
      </div>

      <div className="job-detail-row">
        <strong>Command:</strong>
        <div className="command-box">{job.command}</div>
      </div>

      <div className="job-detail-row">
        <strong>Docker Image:</strong>
        <span>{job.image}</span>
      </div>

      <div className="job-detail-row">
        <strong>Schedule:</strong>
        <span>{readableSchedule(job.schedule)}</span>
      </div>

      <div className="job-detail-row">
        <strong>Files:</strong>
        <div className="file-list">
          {files.length === 0 && <span>No files uploaded</span>}
          {files.map((file, index) => {
            const name = file.filename
              ? file.filename.split("/").pop()
              : file.file?.split("/").pop() || "(no name)"

            return (
              <div className="file-item" key={`${file.id ?? 'temp'}-${index}`}>
                <span className="file-icon">📄</span>
                <span className="file-name">{name}</span>
              </div>
            )
          })}
        </div>
      </div>


    </div>
    <div className="job-runs-card">
      <h2>Recent Runs</h2>

      {loadingJobRuns ? (
        <p>Loading job runs...</p>
      ) : jobRuns.length === 0 ? (
        <p>No runs yet</p>
      ) : (
        <table className="job-runs-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Status</th>
              <th>Started At</th>
              <th>Finished At</th>
              <th>Duration (s)</th>
              <th>Actions</th>
            </tr>
          </thead>
          
          <tbody>
            {jobRuns.map((run) => (
              <tr key={run.id}>
                <td>{run.id}</td>
                <td>
                  <span className={`run-status ${run.status.toLowerCase()}`}>
                    <span className="status-icon">
                      {run.status.toLowerCase() === "success" && "✓"}
                      {run.status.toLowerCase() === "failed" && "✗"}
                      {run.status.toLowerCase() === "running" && "↻"}
                      {run.status.toLowerCase() === "pending" && "⧗"}
                      {run.status.toLowerCase() === "cancelled" && "⏹"}
                    </span>
                    <span className="status-text">
                      {run.status}
                    </span>
                  </span>
                </td>
                <td>{run.started_at ? new Date(run.started_at).toLocaleString() : "N/A"}</td>
                <td>{run.finished_at ? new Date(run.finished_at).toLocaleString() : "N/A"}</td>
                <td>{run.duration_seconds !== null ? run.duration_seconds.toFixed(2) : "N/A"}</td>
                <td>
                  <button
                    className="view-job-run-btn"
                    onClick={() => navigate(`/jobs/runs/${run.id}`)}
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  </div>
)
}