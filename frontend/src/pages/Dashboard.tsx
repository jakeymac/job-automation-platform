import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { apiFetch } from "../api/client"
import StatusBadge from "../components/StatusBadge"

interface Job {
  id: number
  name: string
  schedule: string
  is_active: boolean
  last_run_status: string | null
}

export default function JobsPage() {
  const { isAuthenticated } = useAuth()
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)

  const navigate = useNavigate()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login")
    }
    async function loadJobs() {
      try {
        const response = await apiFetch('/jobs/')
        const data = await response.json()
        console.log("Loaded jobs:", data)
        setJobs(data)
      } catch (err) {
        console.error("Failed to load jobs", err)
      } finally {
        setLoading(false)
      }
    }

    loadJobs()
  }, [isAuthenticated])

  if (loading) {
    return <p>Loading jobs...</p>
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Jobs</h1>
        <button
          onClick={() => navigate("/jobs/new")}
          aria-label="Create new job"
          className="plus-btn"
        >
          +
        </button>
      </div>

      <table className="jobs-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Schedule</th>
            <th>Last Run Status</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {jobs.map((job) => (
            <tr key={job.id}>
              <td>{job.name}</td>
              <td>{job.schedule}</td>
              <td>
                {job.last_run_status ? (
                  <StatusBadge status={job.last_run_status} />
                ) : (
                  "N/A"
                )}
              </td>
              <td>
                <button>Run</button>
                <button onClick={() => navigate(`/jobs/${job.id}`)}>View</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}