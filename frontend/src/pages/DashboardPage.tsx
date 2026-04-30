import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { apiFetch } from "../api/client"
import { usePageTitle } from "../hooks/usePageTitle"
import { useRequireAuth } from "../hooks/useRequireAuth"
import StatusBadge from "../components/StatusBadge"
import ConfirmationModal from "../components/ConfirmationModal"

interface Job {
  id: number
  name: string
  schedule: string
  is_active: boolean
  last_run_status: string | null
}

export default function JobsPage() {
  const { isAuthenticated, authLoading } = useRequireAuth()
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [jobIDToDelete, setJobIDToDelete] = useState<number | null>(null)

  const navigate = useNavigate()

  usePageTitle("Home")

  useEffect(() => {
    let interval: number

    async function loadJobs() {
      try {
        const response = await apiFetch('/jobs/')
        if (response.status === 401) {
          navigate("/login")
          return
        }
        const data = await response.json()
        if (!Array.isArray(data)) {
          console.error("Invalid jobs response:", data)
          setJobs([])
          return
        }
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
  }, [isAuthenticated, authLoading, navigate])

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

  async function handleDeleteJob() {
    if (jobIDToDelete === null) return

    try {
      const response = await apiFetch(`/jobs/${jobIDToDelete}/delete/`, {
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
                <button className="run-job-btn" onClick={() => handleRunJob(job.id)}>Run</button>
                <button className="view-job-btn" onClick={() => navigate(`/jobs/${job.id}`)}>View</button>
                <button 
                  className="job-delete-btn" 
                  onClick={() => {
                    setJobIDToDelete(job.id)
                    setDeleteModalOpen(true)
                  }
                }
                >Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <ConfirmationModal
        isOpen={deleteModalOpen}
        title="Confirm Delete"
        message="Are you sure you want to delete this job?"
        onConfirm={handleDeleteJob}
        onCancel={() => setDeleteModalOpen(false)}
      />
    </div>
  )
}