import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { apiFetch } from "../api/client"
import { readableSchedule } from "../utils/cron"
import cronstrue  from "cronstrue"


interface Job {
  id: number
  name: string
  description: string
  schedule: string
  status: string
  is_active: boolean
}

export default function ViewJobDetails() {
  const { id } = useParams()
  const [job, setJob] = useState<Job | null>(null)
  const [loading, setLoading] = useState(true)

  const navigate = useNavigate()


  useEffect(() => {
    async function loadJob() {
      try {
        const response = await apiFetch(`http://127.0.0.1:8000/api/jobs/${id}/`)
        if (!response.ok) {
          throw new Error("Failed to load job")
        }
        const data = await response.json()
        
        setJob(data)
      } catch {
        console.error("Failed to load job")
      } finally {
        setLoading(false)
      }
    }

    loadJob()
  }, [id])

  if (loading) {
    return <div className="job-details-page">Loading job...</div>
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

          <button className="job-run-btn">
            Run
          </button>
        </div>
      </div>

      <div className="job-detail-row">
        <strong>Description:</strong>
        <span>{job.description}</span>
      </div>

      <div className="job-detail-row">
        <strong>Schedule:</strong>
        <span>{readableSchedule(job.schedule)}</span>
      </div>

    </div>
  </div>
)
}