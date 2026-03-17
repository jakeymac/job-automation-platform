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
  const [image, setImage] = useState("python:3.11-slim")
  const [command, setCommand] = useState("")
  const [files, setFiles] = useState<FileList | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([])
  const [uploading, setUploading] = useState(false)
  

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
        setImage(data.image)
        setCommand(data.command)

        // load existing files
        const filesResponse = await apiFetch(`http://127.0.0.1:8000/api/jobs/${id}/files/`)
        if (filesResponse.ok) {
          const filesData = await filesResponse.json()
          setUploadedFiles(filesData)
        }
      } catch {
        console.error("Failed to load job")
      } finally {
        setLoading(false)
      }
    }

    loadJob()
  }, [id])

  async function handleFileUpload(file: File | null) {
    if (!file) return

    setUploading(true)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await apiFetch(
        `http://127.0.0.1:8000/api/jobs/${id}/files/upload/`,
        {
          method: "POST",
          body: formData,
        }
      )

      if (!response.ok) {
        throw new Error("Upload failed")
      }

      const newFile = await response.json()

      setUploadedFiles((prev) => [...prev, newFile])
    } catch (err) {
      console.error(err)
      alert("File upload failed")
    } finally {
      setUploading(false)
    }
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)

    const formData = new FormData()
    formData.append("name", name)
    formData.append("description", description)
    formData.append("schedule", schedule)
    formData.append("is_active", String(isActive))
    formData.append("image", image)
    formData.append("command", command)

    try {
      const response = await apiFetch(`http://127.0.0.1:8000/api/jobs/${id}/edit/`, {
        method: "PATCH",
        body: formData
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
          <label>Command</label>
          <textarea
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="e.g. python script.py"
          />
        </div>

        <div className="form-field">
          <label>Docker Image</label>
          <input
          value={image}
          onChange={(e) => setImage(e.target.value)}
          placeholder="e.g. python:3.11-slim"
          />
        </div>
        <div className="form-field">
          <label>Upload Files</label>
          <input
          type="file"
          onChange={(e) => {
            const selected = e.target.files ? e.target.files[0] : null
            setFiles(e.target.files)
            handleFileUpload(selected)
          }}
          />
          {uploading && <small>Uploading...</small>}
        </div>
        <div className="form-field">
          <label>Current Files</label>
          {uploadedFiles.length === 0 && <small>No files uploaded</small>}
          <ul>
            {uploadedFiles.map((f, index) => (
              <li key={`${f.id ?? 'temp'}-${index}`}>
                {f.filename ? f.filename.split("/").pop() : f.file?.split("/").pop() || "(no name)"}
              </li>
            ))}
          </ul>
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