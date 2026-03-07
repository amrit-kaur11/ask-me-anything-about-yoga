import React from "react";

export function MessageBubble({ role, content, isUnsafe, safetyReasons }) {
  const isUser = role === "user";
  
  return (
    <div style={{ marginTop: 18 }}>
      {isUnsafe && (
        <div
          style={{
            marginTop: 20,
            padding: 14,
            borderRadius: 10,
            border: "1px solid #cc0000",
            background: "#ffe6e6",
            marginBottom: 14
          }}
        >
          <strong>Safety Warning:</strong> This question may involve risk without personalized guidance.
          {safetyReasons && safetyReasons.length > 0 && (
            <div style={{ marginTop: 8, color: "#660000" }}>
              <strong>Flagged for:</strong> {safetyReasons.join(", ")}
            </div>
          )}
        </div>
      )}

      <div style={{ padding: 14, borderRadius: 10, border: "1px solid #ddd", background: isUser ? "#f0f9ff" : "transparent" }}>
        <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5 }}>{content}</div>
      </div>
    </div>
  );
}
