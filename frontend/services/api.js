const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function fetchAPI(endpoint, options = {}) {
  try {
    const token = sessionStorage.getItem("token");

    const response = await fetch(`${API_URL}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }

    // Handle 204 No Content
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

// Task API functions
export async function getTasks(params = {}) {
  const queryParams = new URLSearchParams();
  if (params.page) queryParams.append("page", params.page);
  if (params.status) queryParams.append("status", params.status);
  if (params.search) queryParams.append("search", params.search);

  const query = queryParams.toString();
  return fetchAPI(`/tasks${query ? `?${query}` : ""}`);
}

export async function getTask(taskId) {
  return fetchAPI(`/tasks/${taskId}`);
}

export async function createTask(taskData) {
  return fetchAPI("/tasks", {
    method: "POST",
    body: JSON.stringify(taskData),
  });
}

export async function updateTask(taskId, taskData) {
  return fetchAPI(`/tasks/${taskId}`, {
    method: "PUT",
    body: JSON.stringify(taskData),
  });
}

export async function completeTask(taskId) {
  return fetchAPI(`/tasks/${taskId}/complete`, {
    method: "PATCH",
  });
}

export async function uncompleteTask(taskId) {
  return fetchAPI(`/tasks/${taskId}/uncomplete`, {
    method: "PATCH",
  });
}

export async function deleteTask(taskId) {
  return fetchAPI(`/tasks/${taskId}`, {
    method: "DELETE",
  });
}

export async function clearCompletedTasks(page = null) {
  const query = page ? `?page=${encodeURIComponent(page)}` : "";
  return fetchAPI(`/tasks/completed/clear${query}`, {
    method: "DELETE",
  });
}

export async function reorderTasks(taskIds) {
  return fetchAPI("/tasks/reorder", {
    method: "PUT",
    body: JSON.stringify({ task_ids: taskIds }),
  });
}

// Page API functions
export async function getPages() {
  return fetchAPI("/pages");
}

export async function createPage(name, sharedWith = []) {
  return fetchAPI("/pages", {
    method: "POST",
    body: JSON.stringify({ name, shared_with: sharedWith }),
  });
}

export async function updatePage(pageId, data) {
  return fetchAPI(`/pages/${pageId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deletePage(pageId) {
  return fetchAPI(`/pages/${pageId}`, {
    method: "DELETE",
  });
}

// AI API functions
export async function getAIStatus() {
  return fetchAPI("/ai/health");
}

export async function chatWithAI(message, provider = null) {
  return fetchAPI("/ai/chat", {
    method: "POST",
    body: JSON.stringify({ message, provider }),
  });
}

export async function suggestTasks(prompt) {
  return fetchAPI("/ai/suggest-tasks", {
    method: "POST",
    body: JSON.stringify({ prompt }),
  });
}
