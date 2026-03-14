import React, { useMemo, useState } from "react";
import { askYoga, sendFeedback } from "./api.js";
import { MessageBubble } from "./components/MessageBubble";
import { SourceList } from "./components/SourceList";
import { Feedback } from "./components/Feedback";

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
      const msg = String(e.message || e);
      if (msg.toLowerCase().includes("abort") || msg.toLowerCase().includes("failed to fetch")) {
        setError("The server is waking up from sleep. Please wait 30 seconds and try again.");
      } else {
        setError(msg);
      }
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

      <div style={{ maxWidth: 900, margin: "0 auto", background: theme.card, borderRadius: 20, padding: 24, boxShadow: "0 10px 30px rgba(0,0,0,0.08)", position: "relative" }}>

        <h1 style={{ textAlign: "center", marginBottom: 8, fontSize: 32, fontWeight: 700, letterSpacing: "-0.02em" }}>🧘 AskMe AI — Yoga</h1>
        <p style={{ textAlign: "center", color: theme.subText, marginBottom: 24, maxWidth: 560, margin: "0 auto 24px", lineHeight: 1.6, fontSize: 15 }}>
          Ask anything about yoga, wellness, and mindfulness. The app retrieves relevant notes (“sources used”) and shows safety warnings when needed.
        </p>

        {/* Input */}
        <div style={{ display: "flex", gap: 12, marginTop: 28 }}>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything about yoga..."
            rows={3}
            style={{
              flex: 1,
              padding: 14,
              fontSize: 15,
              borderRadius: 14,
              border: `1px solid ${theme.border}`,
              outline: "none",
              background: dark ? "#020617" : "white",
              color: theme.text,
              transition: "all 0.2s ease",
              boxShadow: "none"
            }}
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

        {/* Loading */}
        {loading && (
          <div style={{ marginTop: 20, padding: 14, borderRadius: 10, border: "1px solid #ddd" }}>
            <div style={{ height: 10, background: "#eee", borderRadius: 8, marginBottom: 10 }} />
            <div style={{ height: 10, background: "#eee", borderRadius: 8, marginBottom: 10, width: "80%" }} />
            <div style={{ height: 10, background: "#eee", borderRadius: 8, width: "60%" }} />
          </div>
        )}

        {/* Results */}
        {!loading && (answer || isUnsafe) && (
          <>
            <MessageBubble
              role="assistant"
              content={answer}
              isUnsafe={isUnsafe}
              safetyReasons={safetyReasons}
            />
            <SourceList sources={sources} />
            <Feedback
              requestId={requestId}
              onFeedback={onFeedback}
              feedbackState={feedbackState}
            />
          </>
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
    </div>
  );
}
