import { useEffect, useState } from "react"
import { apiFetch } from "../api/client"
import { usePageTitle } from "../hooks/usePageTitle"
import { useRequireAuth } from "../hooks/useRequireAuth"

export default function ViewAccountPage() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [isEditing, setIsEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState<Record<string, string[]>>({})
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
  })
  const hasChanges = user ? (
    formData.first_name.trim() !== (user.first_name || "").trim() ||
    formData.last_name.trim() !== (user.last_name || "").trim() ||
    formData.email.trim() !== (user.email || "").trim()
  ) : false

  usePageTitle("Account Details")
  useRequireAuth()

  function handleChange(field: string, value: string) {
    setFormData((prev) => ({ ...prev, [field]: value }))
    setErrors((prev) => ({ ...prev, [field]: [] }))
  }

  async function handleSave() {
    try {
      setSaving(true)
      const response = await apiFetch("/auth/update-me/", {
        method: "PUT",
        body: JSON.stringify(formData),
      })
      if (!response.ok) {
        const errorData = await response.json()
        setErrors(errorData)
        return
      }

      const data = await response.json()
      setErrors({})
      setUser({
        ...user,
        first_name: data.first_name || "",
        last_name: data.last_name || "",
        email: data.email || "",
      })
      setIsEditing(false)
    } catch (error) {
      console.error("Failed to update account details:", error)
      console.log('error: ', error)
    } finally {
      setSaving(false)
    }
  }

  useEffect(() => {
    async function loadUser() {
      try {
        const response = await apiFetch("/auth/me/")
        const data = await response.json()
        setUser(data)
        setFormData({
          first_name: data.first_name || "",
          last_name: data.last_name || "",
          email: data.email || "",
        })
      } catch (error) {
        console.error("Failed to load user:", error)
      } finally {
        setLoading(false)
      }
    }

    loadUser()
  }, [])

  if (loading) return <div>Loading...</div>
  if (!user) return <div>Failed to load account details.</div>

  return (
    <div className="account-page">
      <div className="account-card">
        <div className="account-header">
          <h1 className="account-title">Account Details</h1>
          {!isEditing && (
            <button className="edit-btn" onClick={() => setIsEditing(true)}>
              Edit
            </button>
          )}
        </div>

        <div className="account-row">
          <strong>Name:</strong>
          {isEditing ? (
            <div>
              <input value={formData.first_name} onChange={(e) => handleChange("first_name", e.target.value)} placeholder="First Name" />
              {errors.first_name && errors.first_name.length > 0 && (
                <div className="field-error">{errors.first_name[0]}</div>
              )}
            </div>
          ) : (
            <span>{user.first_name ? user.first_name : "No First Name Provided"}</span>
          )}
        </div>

        <div className="account-row">
          <strong>Last Name:</strong>
          {isEditing ? (
            <div>
              <input value={formData.last_name} onChange={(e) => handleChange("last_name", e.target.value)} placeholder="Last Name" />
              {errors.last_name && errors.last_name.length > 0 && (
                <div className="field-error">{errors.last_name[0]}</div>
              )}
            </div>
          ) : (
            <span>{user.last_name ? user.last_name : "No Last Name Provided"}</span>
          )}
        </div>
        
        {!isEditing ? (
          <div className="account-row">
            <strong>Username:</strong>
            <span>{user.username}</span>
          </div>
        ) : null}

        <div className="account-row">
          <strong>Email:</strong>
          {isEditing ? (
            <div>
              <input value={formData.email} onChange={(e) => handleChange("email", e.target.value)} placeholder="Email" />
              {errors.email && errors.email.length > 0 && (
                <div className="field-error">{errors.email[0]}</div>
              )}
            </div>
          ) : (
            <span>{user.email}</span>
          )}
        </div>
        
        {errors.non_field_errors && (
          <div className="field-error">{errors.non_field_errors[0]}</div>
        )}
        <div className="account-actions">
          {isEditing ? (
            <>
              <button className={`save-btn ${saving ? "saving" : ""}`} onClick={handleSave} disabled={!hasChanges || saving}>
                {saving ? <div className="spinner"></div> : "Save"}
              </button>
              <button className="cancel-btn" onClick={() => {
                setFormData({
                  first_name: user.first_name || "",
                  last_name: user.last_name || "",
                  email: user.email || "",
                })
                setIsEditing(false)
              }}>Cancel</button>
            </>
          ) : null}
        </div>
      </div>
    </div>
  )
}