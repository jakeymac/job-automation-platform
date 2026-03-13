import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import { useAuth } from "../context/AuthContext"
import { apiFetch } from "../api/client"

interface Job {
  id: number
  name: string
  description: string
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
        const response = await apiFetch("http://127.0.0.1:8000/api/jobs/")
        const data = await response.json()
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
    <div>
      <h2>Jobs</h2>

      {jobs.length === 0 && <p>No jobs yet.</p>}

      <ul>
        {jobs.map((job) => (
          <li key={job.id}>
            <strong>{job.name}</strong> — {job.description}
          </li>
        ))}
      </ul>
    </div>
  )
}