import React from "react";
import ReactMarkdown from "react-markdown";

export function MessageBubble({ role, content, isUnsafe, safetyReasons }) {
  const isUser = role === "user";

  // Fix <br> tags returned by the API
  const cleanContent = content.replace(/<br\s*\/?>/gi, "\n");

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
            marginBottom: 14,
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

      <div
        style={{
          padding: 14,
          borderRadius: 10,
          border: "1px solid #ddd",
          background: isUser ? "#f0f9ff" : "transparent",
        }}
      >
        {/* ✅ ReactMarkdown renders bold, tables, bullets properly */}
        <div style={{ lineHeight: 1.7 }}>
          <ReactMarkdown
            components={{
              // ✅ Style tables nicely
              table: ({ node, ...props }) => (
                <table
                  style={{
                    width: "100%",
                    borderCollapse: "collapse",
                    marginTop: 10,
                    marginBottom: 10,
                    fontSize: 14,
                  }}
                  {...props}
                />
              ),
              th: ({ node, ...props }) => (
                <th
                  style={{
                    border: "1px solid #ccc",
                    padding: "8px 12px",
                    background: "#f3f4f6",
                    textAlign: "left",
                    fontWeight: 600,
                  }}
                  {...props}
                />
              ),
              td: ({ node, ...props }) => (
                <td
                  style={{
                    border: "1px solid #ccc",
                    padding: "8px 12px",
                  }}
                  {...props}
                />
              ),
            }}
          >
            {cleanContent}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}