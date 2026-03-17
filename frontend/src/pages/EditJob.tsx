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
}

export default function EditJobPage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [job, setJob] = useState<Job | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [schedule, setSchedule] = useState("")
  const [isActive, setIsActive] = useState(false)

  useEffect(() => {
    async function loadJob() {
      try {
        const response = await apiFetch(`http://127.0.0.1:8000/api/jobs/${id}/`)
        if (!response.ok) {
          throw new Error("Failed to load job")
        } 

        const data = await response.json()

        setJob(data)

        // populate form fields
        setName(data.name)
        setDescription(data.description)
        setSchedule(data.schedule)
        setIsActive(data.is_active)

      } catch {
        console.error("Failed to load job")
      } finally {
        setLoading(false)
      }
    }

    loadJob()
  }, [id])

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)

    try {
      const response = await apiFetch(`http://127.0.0.1:8000/api/jobs/${id}/edit/`, {
        method: "PATCH",
        body: JSON.stringify({
          name,
          description,
          schedule,
          is_active: isActive
        })
      })

      if (!response.ok) {
        throw new Error("Failed to save job")
      }

      navigate(`/jobs/${id}`)

    } catch {
      alert("Failed to save job")
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="job-details-page">Loading job...</div>
  }

  if (!job) {
    return <div className="job-details-page">Job not found</div>
  }

  return (
    <div className="job-details-page">
      <form className="job-edit-card" onSubmit={handleSave}>

        <div className="job-header">
          <h1 className="job-title">Edit Job</h1>
        </div>

        <div className="form-field">
          <label>Name</label>
          <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          />
        </div>

        <div className="form-field">
          <label>Description</label>
          <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div className="form-field">
          <label>Schedule (cron)</label>
          <input
          value={schedule}
          onChange={(e) => setSchedule(e.target.value)}
          />
          <small>{readableSchedule(schedule)}</small>
        </div>

        <div className="form-field checkbox-field">
          <label>
          <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
          />
          Active
          </label>
        </div>

        <div className="job-form-actions">
          <button
          type="button"
          className="cancel-btn"
          onClick={() => navigate(`/jobs/${id}`)}
          >
          Cancel
          </button>

          <button
          type="submit"
          className="save-btn"
          disabled={saving}
          >
          {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>

      </form>
    </div>
  )
}