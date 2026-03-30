import { useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export function requireAuth() {
  const { authLoading, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (authLoading) return

    if (!isAuthenticated) {
      navigate("/login")
    }
  }, [authLoading, isAuthenticated])

  return { authLoading, isAuthenticated }
}