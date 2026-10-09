const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function fetchAuth(endpoint, options = {}) {
  try {
    // Use sessionStorage so authentication only lasts for the current tab session.
    // When the user opens a new tab, they will be asked to log in again.
    const token = sessionStorage.getItem("token");

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  } catch (error) {
    if (error.name === "TypeError" && error.message === "Failed to fetch") {
      throw new Error("Cannot connect to the server. Please make sure the backend is running.");
    }
    throw error;
  }
}

export async function register(username, password) {
  return fetchAuth("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export async function login(username, password) {
  const data = await fetchAuth("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });

  if (data.access_token) {
    // Store token in sessionStorage so it only lasts for the current tab session.
    sessionStorage.setItem("token", data.access_token);
    sessionStorage.setItem("user", JSON.stringify(data.user));
  }

  return data;
}

export async function logout() {
  sessionStorage.removeItem("token");
  sessionStorage.removeItem("user");
}

export async function getCurrentUser() {
  return fetchAuth("/auth/me");
}

export function isAuthenticated() {
  return !!sessionStorage.getItem("token");
}

export function getUser() {
  const user = sessionStorage.getItem("user");
  return user ? JSON.parse(user) : null;
}
