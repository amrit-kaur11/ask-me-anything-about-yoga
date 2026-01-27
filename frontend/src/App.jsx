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
  const [dark, setDark] = useState(false);

  const canAsk = useMemo(() => query.trim().length >= 3 && !loading, [query, loading]);
  // ⏳ Animated loading dots (UI only)
  const LoadingDots = () => {
    const [dots, setDots] = useState(".");

    React.useEffect(() => {
      const id = setInterval(() => {
        setDots((d) => (d.length === 3 ? "." : d + "."));
      }, 500);
      return () => clearInterval(id);
    }, []);

    return <span>Thinking{dots}</span>;
  };

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

  // 🎨 THEME COLORS 
  const theme = {
  bg: dark
  ? "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
  : "linear-gradient(135deg, #e8f5e9, #f1f8e9, #e3f2fd)",
  card: dark ? "#1e293b" : "rgba(255,255,255,0.9)",
  text: dark ? "#e5e7eb" : "#1f2937",
  subText: dark ? "#9ca3af" : "#4e6e5d",
  border: dark ? "#334155" : "#c8e6c9",
  answerBg: dark ? "#0f172a" : "#f1f8e9",
  button: dark
  ? "linear-gradient(135deg, #6366f1, #4f46e5)"
  : "linear-gradient(135deg, #43a047, #2e7d32)",
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: dark
          ? "linear-gradient(180deg, #0b1220, #0f172a)"
          : "linear-gradient(135deg, #e8f5e9, #f1f8e9, #e3f2fd)",
        padding: "40px 16px",
        fontFamily: "system-ui, Arial",
        color: theme.text,
        transition: "all 0.3s ease",
      }}
    >
      {/* 🌼Decorative flower / leaf SVGs */}
      <svg 
        width="260"
        height="260"
        viewBox="0 0 200 200"
        style={{
        position: "fixed",
        top: -40,
        left: -40,
        opacity: dark ? 0.12 : 0.18,
        pointerEvents: "none",
        }}
      >
        <path
          fill="#81c784"
          d="M39.8,-68.3C51.5,-61.5,60.6,-51.2,67.6,-39.2C74.6,-27.2,79.6,-13.6,78.7,-0.5C77.8,12.7,71,25.4,62.6,36.5C54.2,47.7,44.3,57.3,32.6,63.3C21,69.2,7.5,71.6,-6.2,71.5C-19.9,71.4,-39.8,68.8,-52.7,60.2C-65.6,51.6,-71.6,36.9,-74.1,22.2C-76.6,7.6,-75.6,-7,-70.1,-19.3C-64.6,-31.7,-54.6,-41.8,-42.9,-48.9C-31.2,-56,-15.6,-60.1,-0.4,-59.5C14.8,-58.8,29.6,-53.1,39.8,-68.3Z"
          transform="translate(100 100)"
        />
      </svg>

      <svg
        width="220"
        height="220"
        viewBox="0 0 200 200"
        style={{
        position: "fixed",
        bottom: -40,
        right: -40,
        opacity: dark ? 0.12 : 0.18,
        pointerEvents: "none",
        }}
        >
        <path
         fill="#aed581"
         d="M41.3,-66.5C53.7,-60.5,63.7,-50.5,69.6,-38.4C75.4,-26.3,77.2,-13.1,75.8,-0.8C74.3,11.6,69.7,23.2,62.1,33.3C54.5,43.5,43.8,52.1,31.7,57.6C19.6,63.1,6.1,65.5,-7.8,67.3C-21.6,69.1,-43.2,70.2,-56.2,62.6C-69.3,55,-73.8,38.7,-76.1,23.3C-78.4,7.8,-78.4,-6.8,-72.6,-18.5C-66.9,-30.3,-55.4,-39.3,-43,-45.9C-30.7,-52.6,-15.3,-56.8,-0.1,-56.6C15.2,-56.4,30.3,-51.9,41.3,-66.5Z"
         transform="translate(100 100)"
       />
     </svg>

      {/* 🌙 Dark mode toggle */}
      <button
        onClick={() => setDark(!dark)}
        style={{
          position: "absolute",
          top: 14,
          right: 14,
          border: "none",
          borderRadius: 8,
          padding: "6px 10px",
          cursor: "pointer",
          background: dark ? "#1e293b" : "#e8f5e9",
          color: dark ? "#e5e7eb" : "#1f2937",
          fontSize: 13,
          fontWeight: 600,
          boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
        }}
      >
        {dark ? "🌞 Light" : "🌙 Dark"}
      </button>

      <div style={{position: "fixed", inset: 0, pointerEvents: "none", background: "radial-gradient(circle at 10% 20%, rgba(129,199,132,0.15), transparent 40%)," + "radial-gradient(circle at 90% 80%, rgba(174,213,129,0.15), transparent 40%)"}}/>
       <div style={{maxWidth: 900, margin: "0 auto", background: "rgba(255,255,255,0.85)", borderRadius: 20, padding: 24, boxShadow: "0 10px 30px rgba(0,0,0,0.08)", position: "relative"}}></div>
        <h1 style={{ textAlign: "center" , marginBottom: 8 , fontSize: 32, fontWeight: 700, letterSpacing: "-0.02em", }}>🧘AskMe AI — Yoga</h1>
        <p style={{ textAlign: "center", color: "theme.subText" , marginBottom: 24, maxWidth: 560, margin: "0 auto 24px" , lineHeight: 1.6 , fontSize: 15 }}>
        Ask anything about yoga, wellness, and mindfulness. The app retrieves relevant notes (“sources used”) and shows safety warnings when needed.
        </p>

      {/* Input */}
      <div style={{ display: "flex", gap: 12, marginTop: 28 }}>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything about yoga..."
          rows={3}
          style={{ flex: 1, padding: 14, fontSize: 15, borderRadius: 14, border: `1px solid ${theme.border}`, outline: "none" , background: dark ? "#020617" : "white", color: theme.text, transition: "all 0.2s ease", boxShadow: "none" }}
          onFocus={(e) => {
            e.currentTarget.style.boxShadow = dark
              ? "0 0 0 3px rgba(99,102,241,0.35)"
              : "0 0 0 3px rgba(67,160,71,0.35)";
          }}
          onBlur={(e) => {
            e.currentTarget.style.boxShadow = "none";
          }}
        />
        <button
          onClick={onAsk}
          disabled={!canAsk}
          style={{
            width: 150,
            borderRadius: 14,
            border: "none",
            background: canAsk ? theme.button : "#94a3b8",
            color: "white",
            fontWeight: 600,
            cursor: canAsk ? "pointer" : "not-allowed",
            boxShadow: canAsk
              ? "0 6px 16px rgba(46,125,50,0.35)"
              : "none",
          }}
          onMouseDown={(e) => {
            if (canAsk) e.currentTarget.style.transform = "scale(0.97)";
          }}
          onMouseUp={(e) => {
            e.currentTarget.style.transform = "scale(1)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "scale(1)";
          }}
        >
          {loading ? <LoadingDots /> : "Ask"}
        </button>
      </div>
      
      {/* Error */}
      {error && (
        <div style={{ marginTop: 16, padding: "12px 14px", borderRadius: 12, background: dark ? "#3f1d1d" : "#fdecea", border: dark ? "1px solid #7f1d1d" : "1px solid #f5c6cb", color: dark ? "#fecaca" : "#7f1d1d", fontSize: 14 }}>
          <strong>Notice:</strong> {error}
        </div>
      )}

      {loading && (
        <div style={{ marginTop: 20, padding: 14, borderRadius: 10, border: "1px solid #ddd" }}>
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
                marginTop:20,
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

      <footer
        style={{
        marginTop: 48,
        textAlign: "center",
        fontSize: 13,
        color: theme.subText,
        }}
        >
        🌿 Calm UI • RAG • FastAPI • React
        </footer>
      </div>
  );
}
