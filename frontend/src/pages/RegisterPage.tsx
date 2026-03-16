import { useState, useEffect } from "react"
import { useNavigate } from "react-router"
import { apiFetch } from "../api/client"

export default function RegisterPage() {
  const navigate = useNavigate()

  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  const [checkingUsername, setCheckingUsername] = useState(false)
  const [usernameValid, setUsernameValid] = useState<boolean | null>(null)
  const [usernameError, setUsernameError] = useState<string | null>(null)

  const [checkingEmail, setCheckingEmail] = useState(false)
  const [emailValid, setEmailValid] = useState<boolean | null>(null)
  const [emailError, setEmailError] = useState<string | null>(null)

  const [passwordValid, setPasswordValid] = useState<boolean | null>(null)
  const [passwordError, setPasswordError] = useState<string | null>(null)

  const formValid = 
    usernameValid === true && username !== "" &&
    emailValid === true && email !== "" &&
    passwordValid === true && password !== "" &&
    !checkingUsername && !checkingEmail && !loading

  async function checkUsername(name: string) {
    if (!name) return
    setCheckingUsername(true)

    try {
      const response = await apiFetch(
        `http://127.0.0.1:8000/api/auth/username-valid/?username=${name}`
      )
      
      const data = await response.json()
      setUsernameValid(data.valid)
      setUsernameError(data.error || null)
    } catch {
      setUsernameValid(null)
      setUsernameError("Failed to check username")
    } finally {
      setCheckingUsername(false)
    }
  }

  async function checkEmail(email: string) {
    if (!email) return
    setCheckingEmail(true)

    try {
      const response = await apiFetch(
        `http://127.0.0.1:8000/api/auth/email-valid/?email=${email}`
      )
      const data = await response.json()
      setEmailValid(data.valid)
      setEmailError(data.error || null)
    } catch {
      setEmailValid(null)
      setEmailError("Failed to check email")
    } finally {
      setCheckingEmail(false)
    }
  }

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

  useEffect(() => {
    if (!username) {
      setUsernameValid(null)
      return
    }

    const delayDebounce = setTimeout(() => {
      checkUsername(username)
    }, 500)

    return () => clearTimeout(delayDebounce)
  }, [username])

  useEffect(() => {
    if (!email) {
      setEmailValid(null)
      return
    }

    const delayDebounce = setTimeout(() => {
      checkEmail(email)
    }, 500)
    
    return () => clearTimeout(delayDebounce)
  }, [email])

  useEffect(() => {
    if (!password) {
      setPasswordValid(null)
      return
    }

    const delayDebounce = setTimeout(() => {
      if (password.length < 8 || password.includes(" ")) {
        setPasswordValid(false)
        setPasswordError("Password must be at least 8 characters and contain no spaces")
      } else {
        setPasswordValid(true)
        setPasswordError(null)
      }
    }, 500)

    return () => clearTimeout(delayDebounce)
  }, [password])

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleRegister}>
        <h2>Create Account</h2>

        <div className="auth-input-wrapper">
          <input
            placeholder="Username"
            value={username}
            onChange={(e) => {
              setUsername(e.target.value)
              setUsernameValid(null)
            }}
          />
          {checkingUsername && <span className="input-spinner"></span>}
          {!checkingUsername && usernameValid === true && (
            <span className="input-check">✓</span>
          )}

          {!checkingUsername && usernameValid === false && (
            <span className="input-error-icon">✗</span>
          )}
        </div>
        {usernameValid === false && (
          <div className="field-error">{usernameError}</div>
        )}
        
        <div className="auth-input-wrapper">
            <input
              placeholder="Email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                setEmailValid(null)
              }}
            />
            {checkingEmail && <span className="input-spinner"></span>}
            {!checkingEmail && emailValid === true && (
              <span className="input-check">✓</span>
            )}

            {!checkingEmail && emailValid === false && (
              <span className="input-error-icon">✗</span>
            )}
        </div>
        {emailValid === false && (
          <div className="field-error">{emailError}</div>
        )}
        <div className="auth-input-wrapper">
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {!passwordValid && password !== "" && (
            <span className="input-error-icon">✗</span>
          )}
          {passwordValid && password !== "" && (
            <span className="input-check">✓</span>
          )}
          
        </div>
        {passwordValid === false && (
          <div className="field-error">{passwordError}</div>
        )}
        

        <button type="submit" disabled={!formValid} className="auth-submit-btn register-submit-btn">
          {loading ? <span className="spinner"></span> : "Register"}
        </button>
      </form>
    </div>
  )
}