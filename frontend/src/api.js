// frontend/src/api.js

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  // Try to parse JSON even on errors
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }

  if (!res.ok) {
    const message =
      (data && (data.detail || data.error || data.message)) ||
      `Request failed: ${res.status}`;
    throw new Error(message);
  }
  return data;
}

export async function askYoga(query) {
  return request("/api/ask", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

// rating: "up" | "down"
export async function sendFeedback({ request_id, rating, comment = "" }) {
  return request("/api/feedback", {
    method: "POST",
    body: JSON.stringify({ request_id, rating, comment }),
  });
}
