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
      return
    }

    let interval: number

    async function loadJobs() {
      try {
        const response = await apiFetch('/jobs/')
        const data = await response.json()
        setJobs(data)
      } catch (err) {
        console.error("Failed to load jobs", err)
      } finally {
        setLoading(false)
      }
    }

    // initial load
    loadJobs()

    // poll every 2 seconds
    interval = window.setInterval(() => {
      loadJobs()
    }, 2000)

    return () => {
      clearInterval(interval)
    }
  }, [isAuthenticated])

  async function handleRunJob(jobId: number) {
    try {
      const response = await apiFetch(`/jobs/${jobId}/run/`, {
        method: "POST",
      })

      if (!response.ok) {
        throw new Error("Failed to run job")
      }

      // Refresh jobs after triggering run
      const updated = await apiFetch('/jobs/')
      const data = await updated.json()
      setJobs(data)
    } catch (err) {
      console.error("Failed to run job", err)
      alert("Failed to run job")
    }
  }

  async function handleDeleteJob(jobId: number) {
    if (!window.confirm("Are you sure you want to delete this job?")) {
      return
    }
    
    try {
      const response = await apiFetch(`/jobs/${jobId}/delete/`, {
        method: "DELETE",
      })

      if (!response.ok) {
        throw new Error("Failed to delete job")
      }
      // Refresh jobs after deletion
      const updated = await apiFetch('/jobs/')
      const data = await updated.json()
      setJobs(data)
    } catch (err) {
      console.error("Failed to delete job", err)
      alert("Failed to delete job")
    }
  }

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
                <button onClick={() => handleRunJob(job.id)} className="run-job-btn">Run</button>
                <button onClick={() => navigate(`/jobs/${job.id}`)} className="view-job-btn">View</button>
                <button onClick={() => handleDeleteJob(job.id)} className="delete-job-btn">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}