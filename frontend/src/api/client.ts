export function getAuthToken() {
  return localStorage.getItem("access_token")
}

export async function apiFetch(url: string, options: any = {}) {
  const token = getAuthToken()

  let isFormData = options.body instanceof FormData

  const headers: Record<string, string> = {
    ...(options.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }

  if (!isFormData) {
    headers["Content-Type"] = "application/json"
  }

  return fetch(url, {
    ...options,
    headers,
  })
}