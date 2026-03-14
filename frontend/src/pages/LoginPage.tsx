import { useState } from "react"
import { useNavigate } from "react-router"

import { useAuth } from "../context/AuthContext"
import { apiFetch } from "../api/client"


export default function LoginPage() {
  const { login } = useAuth()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await apiFetch("http://127.0.0.1:8000/api/auth/login/", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (response.ok) {
        login(data.access)
        navigate("/")
      } else {
        alert("Login failed: " + (data.detail || "Unknown error"))
      }
    } catch (err) {
      alert("Login request failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleLogin}>
        <h2>Login</h2>
        <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit" disabled={loading} className="login-btn">
          {loading ? <span className="spinner"></span> : "Login"}
        </button>
      </form>
    </div>
  )
}