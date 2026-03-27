export async function apiFetch(url: string, options: any = {}) {
  let accessToken = localStorage.getItem("access_token")
  const refreshToken = localStorage.getItem("refresh_token")

  let isFormData = options.body instanceof FormData
  const API = import.meta.env.VITE_API_URL


  async function performRequest(token: string | null) {
    const headers: Record<string, string> = {
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    }
    if (!isFormData) {
      headers["Content-Type"] = "application/json"
    }
    return fetch(`${API}${url}`, {
      ...options,
      headers

    })
  }

  let response = await performRequest(accessToken)
  if (response.status === 401 && refreshToken) {
    const refreshResponse = await fetch(`${API}/auth/refresh/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    

    if (refreshResponse.ok) {
      const data = await refreshResponse.json()
      localStorage.setItem("access_token", data.access)
      response = await performRequest(data.access)
    } else {
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
      window.location.href = "/login"
      throw new Error("Session expired. Please log in again.")
    }
  }
  return response
}