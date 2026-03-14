import { Link } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function Header() {
  const { isAuthenticated, logout } = useAuth()

  return (
    <header className="header">
      <div className="header-left">
        <Link to="/" className="logo">
          Job Automation
        </Link>

      </div>
      
      <nav className="nav">
        {isAuthenticated ? (
          <>
            <Link to="/">Dashboard</Link>
            <button onClick={logout} className="logout-btn">Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register" className="register-btn">Register</Link>
          </>
        )}
      </nav>
    </header>
  )
}