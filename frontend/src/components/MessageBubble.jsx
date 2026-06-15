import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function MessageBubble({ role, content, isUnsafe, safetyReasons }) {
  const isUser = role === "user";

  const cleanContent = (content || "")
    .toString()

    // Convert literal escaped newlines from JSON/stringified output into real line breaks
    .replace(/\\n/g, "\n")

    // Convert API <br> tags into real line breaks
    .replace(/<br\s*\/?>/gi, "\n")

    // Fix escaped markdown, for example \*\*Purpose\*\* → **Purpose**
    .replace(/\\([*_#`>~\[\]()\-.!])/g, "$1")

    // Clean before removing code fences
    .trim()

    // Remove accidental markdown/code fences from model output
    .replace(/^```(?:markdown)?\s*/i, "")
    .replace(/```\s*$/i, "")

    // Remove duplicate Sources line if backend still sends it
    .replace(/\n?\*\*Sources:\*\*\s*[\w:,\-\s.]+$/i, "")
    .replace(/\n?Sources:\s*[\w:,\-\s.]+$/i, "")

    // Clean extra spacing
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  const cardStyle = {
    marginTop: isUser ? 14 : 18,
    display: "flex",
    justifyContent: isUser ? "flex-end" : "stretch",
  };

  const bubbleStyle = {
    width: isUser ? "fit-content" : "100%",
    maxWidth: isUser ? "78%" : "100%",
    boxSizing: "border-box",
    padding: isUser ? "12px 14px" : "20px 22px",
    borderRadius: isUser ? "16px 16px 4px 16px" : "16px",
    border: isUser ? "1px solid #bfdbfe" : "1px solid #e5e7eb",
    background: isUser ? "#eff6ff" : "#ffffff",
    color: "#111827",
    boxShadow: isUser ? "none" : "0 8px 24px rgba(15, 23, 42, 0.06)",
    overflow: "hidden",
  };

  return (
    <div style={cardStyle}>
      <div style={{ width: isUser ? "auto" : "100%" }}>
        {isUnsafe && (
          <div
            style={{
              marginBottom: 14,
              padding: 14,
              boxSizing: "border-box",
              borderRadius: 12,
              border: "1px solid #fecaca",
              background: "#fef2f2",
              color: "#7f1d1d",
              lineHeight: 1.6,
            }}
          >
            <strong>Safety warning:</strong> This question may involve risk without
            personalized guidance.
            {safetyReasons && safetyReasons.length > 0 && (
              <div style={{ marginTop: 8 }}>
                <strong>Flagged for:</strong> {safetyReasons.join(", ")}
              </div>
            )}
          </div>
        )}

        <div style={bubbleStyle}>
          {!isUser && (
            <div
              style={{
                fontSize: 13,
                fontWeight: 700,
                color: "#166534",
                letterSpacing: "0.02em",
                textTransform: "uppercase",
                marginBottom: 12,
              }}
            >
              Answer
            </div>
          )}

          <div
            style={{
              fontSize: isUser ? 14 : 16,
              lineHeight: 1.75,
            }}
          >
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ node, ...props }) => (
                  <h1
                    style={{
                      margin: "0 0 16px",
                      fontSize: "1.6rem",
                      lineHeight: 1.25,
                      fontWeight: 800,
                      color: "#0f172a",
                    }}
                    {...props}
                  />
                ),
                h2: ({ node, ...props }) => (
                  <h2
                    style={{
                      margin: "24px 0 12px",
                      fontSize: "1.35rem",
                      lineHeight: 1.3,
                      fontWeight: 800,
                      color: "#0f172a",
                      borderBottom: "1px solid #e5e7eb",
                      paddingBottom: 6,
                    }}
                    {...props}
                  />
                ),
                h3: ({ node, ...props }) => (
                  <h3
                    style={{
                      margin: "22px 0 10px",
                      fontSize: "1.12rem",
                      lineHeight: 1.35,
                      fontWeight: 800,
                      color: "#111827",
                    }}
                    {...props}
                  />
                ),
                p: ({ node, ...props }) => (
                  <p
                    style={{
                      margin: "8px 0 12px",
                      lineHeight: 1.75,
                    }}
                    {...props}
                  />
                ),
                ul: ({ node, ...props }) => (
                  <ul
                    style={{
                      margin: "8px 0 14px 16px",
                      paddingLeft: 8,
                      lineHeight: 1.75,
                    }}
                    {...props}
                  />
                ),
                ol: ({ node, ...props }) => (
                  <ol
                    style={{
                      margin: "8px 0 14px 16px",
                      paddingLeft: 8,
                      lineHeight: 1.75,
                    }}
                    {...props}
                  />
                ),
                li: ({ node, ...props }) => (
                  <li
                    style={{
                      marginBottom: 7,
                      paddingLeft: 2,
                    }}
                    {...props}
                  />
                ),
                strong: ({ node, ...props }) => (
                  <strong
                    style={{
                      fontWeight: 800,
                      color: "#0f172a",
                    }}
                    {...props}
                  />
                ),
                blockquote: ({ node, ...props }) => (
                  <blockquote
                    style={{
                      margin: "16px 0",
                      padding: "12px 14px",
                      borderLeft: "4px solid #22c55e",
                      background: "#f0fdf4",
                      borderRadius: "0 10px 10px 0",
                      color: "#14532d",
                    }}
                    {...props}
                  />
                ),
                table: ({ node, ...props }) => (
                  <div
                    style={{
                      overflowX: "auto",
                      margin: "16px 0",
                      border: "1px solid #e5e7eb",
                      borderRadius: 12,
                    }}
                  >
                    <table
                      style={{
                        width: "100%",
                        borderCollapse: "collapse",
                        fontSize: 14,
                        minWidth: 560,
                      }}
                      {...props}
                    />
                  </div>
                ),
                thead: ({ node, ...props }) => (
                  <thead style={{ background: "#f9fafb" }} {...props} />
                ),
                th: ({ node, ...props }) => (
                  <th
                    style={{
                      padding: "10px 12px",
                      borderBottom: "1px solid #e5e7eb",
                      textAlign: "left",
                      fontWeight: 700,
                      color: "#111827",
                    }}
                    {...props}
                  />
                ),
                td: ({ node, ...props }) => (
                  <td
                    style={{
                      padding: "10px 12px",
                      borderBottom: "1px solid #f1f5f9",
                      verticalAlign: "top",
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
    </div>
  );
}