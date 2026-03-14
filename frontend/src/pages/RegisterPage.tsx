import { useState } from "react"
import { useNavigate } from "react-router"
import { apiFetch } from "../api/client"

export default function RegisterPage() {
  const navigate = useNavigate()

  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await apiFetch("http://127.0.0.1:8000/api/auth/register/", {
        method: "POST",
        body: JSON.stringify({ username, email, password }),
      })

      const data = await response.json()

      if (response.ok) {
        alert("Account created successfully")
        navigate("/login")
      } else {
        alert("Registration failed: " + (data.detail || "Unknown error"))
      }
    } catch {
      alert("Registration request failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleRegister}>
        <h2>Create Account</h2>

        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit" disabled={loading} className="login-btn">
          {loading ? <span className="spinner"></span> : "Register"}
        </button>
      </form>
    </div>
  )
}