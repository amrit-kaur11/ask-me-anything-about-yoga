import React, { useMemo, useState } from "react";
import { askYoga, sendFeedback } from "./api.js";

export default function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [isUnsafe, setIsUnsafe] = useState(false);
  const [safetyReasons, setSafetyReasons] = useState([]);
  const [requestId, setRequestId] = useState(null);

  const [feedbackState, setFeedbackState] = useState(null); // "up" | "down" | null
  const [error, setError] = useState("");

  const canAsk = useMemo(() => query.trim().length >= 3 && !loading, [query, loading]);

  async function onAsk() {
    setError("");
    setLoading(true);

    setAnswer("");
    setSources([]);
    setIsUnsafe(false);
    setSafetyReasons([]);
    setRequestId(null);
    setFeedbackState(null);

    try {
      const data = await askYoga(query.trim());
      setAnswer(data.answer || "");
      setSources(data.sources || []);
      setIsUnsafe(Boolean(data.is_unsafe));
      setSafetyReasons(data.safety_reasons || []);
      setRequestId(data.request_id || null);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  async function onFeedback(rating) {
  if (!requestId) {
    setError("Ask a question first, then give feedback.");
    return;
  }

  try {
    setError("");
    await sendFeedback({
      request_id: requestId,   // IMPORTANT: snake_case key expected by backend
      rating,                  // must be "up" or "down"
      comment: ""              // keep as empty string
    });
    setFeedbackState(rating);
  } catch (e) {
    setError(String(e?.message || e));
  }
}


  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: 16, fontFamily: "system-ui, Arial" }}>
      <h1 style={{ marginBottom: 6 }}>AskMe AI — Yoga RAG</h1>
      <p style={{ marginTop: 0, color: "#444" }}>
        Ask anything about yoga. The app retrieves relevant notes (“sources used”) and shows safety warnings when needed.
      </p>

      <div style={{ display: "flex", gap: 10, marginTop: 18 }}>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything about yoga..."
          rows={3}
          style={{ flex: 1, padding: 12, fontSize: 14, borderRadius: 10, border: "1px solid #ccc" }}
        />
        <button
          onClick={onAsk}
          disabled={!canAsk}
          style={{
            width: 140,
            borderRadius: 10,
            border: "1px solid #222",
            background: canAsk ? "#222" : "#999",
            color: "white",
            fontWeight: 600
          }}
        >
          {loading ? "Loading..." : "Ask"}
        </button>
      </div>

      {error && (
        <div style={{ marginTop: 14, padding: 12, borderRadius: 10, background: "#ffecec", border: "1px solid #ffb3b3" }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading && (
        <div style={{ marginTop: 18, padding: 14, borderRadius: 10, border: "1px solid #ddd" }}>
          <div style={{ height: 10, background: "#eee", borderRadius: 8, marginBottom: 10 }} />
          <div style={{ height: 10, background: "#eee", borderRadius: 8, marginBottom: 10, width: "80%" }} />
          <div style={{ height: 10, background: "#eee", borderRadius: 8, width: "60%" }} />
        </div>
      )}

      {!loading && (answer || isUnsafe) && (
        <div style={{ marginTop: 18 }}>
          {isUnsafe && (
            <div
              style={{
                padding: 14,
                borderRadius: 10,
                border: "1px solid #cc0000",
                background: "#ffe6e6",
                marginBottom: 14
              }}
            >
              <strong>Safety Warning:</strong> This question may involve risk without personalized guidance.
              {safetyReasons.length > 0 && (
                <div style={{ marginTop: 8, color: "#660000" }}>
                  <strong>Flagged for:</strong> {safetyReasons.join(", ")}
                </div>
              )}
            </div>
          )}

          <div style={{ padding: 14, borderRadius: 10, border: "1px solid #ddd" }}>
            <h3 style={{ marginTop: 0 }}>Answer</h3>
            <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5 }}>{answer}</div>
          </div>

          <div style={{ marginTop: 14, padding: 14, borderRadius: 10, border: "1px solid #ddd" }}>
            <h3 style={{ marginTop: 0 }}>Sources used</h3>
            {sources.length === 0 ? (
              <div style={{ color: "#666" }}>No sources returned (unsafe flow or retrieval returned none).</div>
            ) : (
              <ol style={{ margin: 0, paddingLeft: 18 }}>
                {sources.map((s) => (
                  <li key={s.chunk_id} style={{ marginBottom: 10 }}>
                    <div><strong>{s.title || "Untitled"}</strong></div>
                    <div style={{ color: "#555" }}>
                      Chunk: {s.chunk_id} • Score: {Number(s.score).toFixed(3)}
                    </div>
                    {s.source && <div style={{ color: "#777" }}>Source: {s.source}</div>}
                  </li>
                ))}
              </ol>
            )}
          </div>

          <div style={{ marginTop: 14, padding: 14, borderRadius: 10, border: "1px solid #ddd" }}>
            <h3 style={{ marginTop: 0 }}>Was this helpful?</h3>
            <div style={{ display: "flex", gap: 10 }}>
              <button
                onClick={() => onFeedback("up")}
                disabled={!requestId || feedbackState !== null}
                style={{ padding: "10px 14px", borderRadius: 10, border: "1px solid #222" }}
              >
                👍
              </button>
              <button
                onClick={() => onFeedback("down")}
                disabled={!requestId || feedbackState !== null}
                style={{ padding: "10px 14px", borderRadius: 10, border: "1px solid #222" }}
              >
                👎
              </button>
              {feedbackState && <div style={{ alignSelf: "center", color: "#444" }}>Thanks for the feedback.</div>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
