import { useState } from "react"
import { useNavigate } from "react-router"

import { useAuth } from "../context/AuthContext"
import { apiFetch } from "../api/client"


export default function LoginPage() {
  const { login } = useAuth()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()

    const response = await apiFetch("http://127.0.0.1:8000/api/auth/login/", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    })
    let data = await response.json()

    if (response.ok) {
      login(data.access)
      navigate("/")
    } else {
      alert("Login failed: " + (data.detail || "Unknown error"))
    }
  }

  return (
    <div>
      <h2>Login</h2>

      <form style={{ display: "flex", flexDirection: "column", gap: "10px", maxWidth: "300px" }} onSubmit={handleLogin}>
        <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Login</button>
      </form>
    </div>
  )
}