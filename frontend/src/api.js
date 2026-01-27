// frontend/src/api.js

/**
* API helper for frontend → backend communication
* Uses Vite dev proxy ("/api" → http://localhost:8000)
* Do NOT use absolute URLs here.
*/

async function request(path, { method = "GET", body, headers, ...rest } = {}) {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;

  const res = await fetch(cleanPath, {
    method,
    mode: "cors",
    headers: {
      Accept: "application/json",
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...(headers || {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
    ...rest,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return res.json();
}

// App.jsx imports these:
export async function askYoga(query) {
  return request("/api/ask", { method: "POST", body: { query } });
}

export async function sendFeedback(payload) {
  // payload should be an object (whatever your backend expects)
  return request("/api/feedback", { method: "POST", body: payload });
}

// optional
export async function health() {
  return request("/api/health");
}
