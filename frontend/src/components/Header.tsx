import { Link } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function Header() {
  const { isAuthenticated, logout } = useAuth()

  return (
    <header
      style={{
        display: "flex",
        justifyContent: "space-between",
        padding: "16px 40px",
        borderBottom: "1px solid #ddd",
      }}
    >
      <Link to="/" style={{ fontWeight: "bold" }}>
        Job Automation
      </Link>

      <nav style={{ display: "flex", gap: "20px" }}>
        {isAuthenticated ? (
          <>
            <Link to="/">Dashboard</Link>
            <button onClick={logout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </nav>
    </header>
  )
}