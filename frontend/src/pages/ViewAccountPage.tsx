import { useEffect, useState } from "react"
import { apiFetch } from "../api/client"
import { useAuth } from "../context/AuthContext"
import { pageTitle } from "../hooks/pageTitle"
import { requireAuth } from "../hooks/requireAuth"
import { useNavigate } from "react-router-dom"

export default function ViewAccountPage() {
  const [user, setUser] = useState<any>(null)
  const { isAuthenticated } = requireAuth()
  const { logout } = useAuth()
  const navigate = useNavigate()

  pageTitle("Account")

  requireAuth()

  useEffect(() => {
    async function loadUser() {
      try {
        const response = await apiFetch("/auth/me/")

        if (response.status === 401) {
          logout()
          navigate("/login")
          return
        }

        const data = await response.json()
        setUser(data)
      } catch (error) {
        console.error("Failed to load user:", error)
      }
    }

    loadUser()
  }, [isAuthenticated])

  if (!user) return <div>Loading...</div>

  return (
    <div className="account-page">
      <div className="account-card">
        <div className="account-header">
          <h1 className="account-title">Account Details</h1>
        </div>

        <div className="account-row">
          <strong>Username:</strong>
          <span>{user.username}</span>
        </div>

        <div className="account-row">
          <strong>Email:</strong>
          <span>{user.email}</span>
        </div>

      </div>
    </div>
  )
}