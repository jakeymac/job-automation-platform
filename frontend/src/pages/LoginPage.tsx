import { useState } from "react"
import { useNavigate } from "react-router"

import { useAuth } from "../context/AuthContext"
import { apiFetch } from "../api/client"
import { usePageTitle } from "../hooks/usePageTitle"


export default function LoginPage() {
  const { login } = useAuth()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const navigate = useNavigate()

  usePageTitle("Login");

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError("") // Clear previous error

    try {
      const response = await apiFetch("/auth/login/", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (response.ok) {
        login(data.access, data.refresh)
        navigate("/")
      } else if (response.status === 401) {
        setError("Invalid username or password")
      } else {
        setError(data.detail || "Login failed")
      }
    } catch (err) {
      setError("An error occurred during login")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleLogin}>
        <h2>Login</h2>
        <input 
          placeholder="Username" 
          value={username} 
          onChange={(e) => {
            setUsername(e.target.value)
            setError("") // Clear error upon user input
          }} 
        />
        <input 
          type="password" 
          placeholder="Password" 
          value={password} 
          onChange={(e) => {
            setPassword(e.target.value)
            setError("") // Clear error upon user input
          }} 
        />
        <button type="submit" disabled={loading} className="auth-submit-btn">
          {loading ? <span className="spinner"></span> : "Login"}
        </button>
        {error && <div className="auth-error">{error}</div>}
      </form>
    </div>
  )
}