import React from "react";

export function SourceList({ sources }) {
  if (!sources || sources.length === 0) {
    return (
      <div
        style={{
          marginTop: 16,
          padding: 18,
          borderRadius: 16,
          border: "1px solid #e5e7eb",
          background: "#ffffff",
          boxShadow: "0 8px 24px rgba(15, 23, 42, 0.04)",
        }}
      >
        <h3 style={{ margin: 0, fontSize: 16, color: "#111827" }}>
          Sources used
        </h3>
        <p style={{ margin: "8px 0 0", color: "#6b7280", fontSize: 14 }}>
          No sources were returned.
        </p>
      </div>
    );
  }

  return (
    <div
      style={{
        marginTop: 16,
        padding: 18,
        borderRadius: 16,
        border: "1px solid #e5e7eb",
        background: "#ffffff",
        boxShadow: "0 8px 24px rgba(15, 23, 42, 0.04)",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "baseline",
          gap: 12,
          marginBottom: 14,
        }}
      >
        <h3 style={{ margin: 0, fontSize: 16, color: "#111827" }}>
          Sources used
        </h3>
        <span style={{ fontSize: 13, color: "#6b7280" }}>
          {sources.length} retrieved
        </span>
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        {sources.map((s, index) => (
          <div
            key={s.chunk_id || `${s.title || "source"}-${index}`}
            style={{
              padding: "12px 14px",
              borderRadius: 12,
              border: "1px solid #edf2f7",
              background: "#f9fafb",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 12,
                alignItems: "flex-start",
              }}
            >
              <div>
                <div
                  style={{
                    fontWeight: 700,
                    color: "#111827",
                    fontSize: 14,
                    lineHeight: 1.4,
                  }}
                >
                  {index + 1}. {s.title || "Untitled source"}
                </div>

                {s.source && (
                  <div
                    style={{
                      marginTop: 4,
                      color: "#6b7280",
                      fontSize: 13,
                      lineHeight: 1.4,
                    }}
                  >
                    {s.source}
                  </div>
                )}
              </div>

              {typeof s.score !== "undefined" && (
                <span
                  style={{
                    whiteSpace: "nowrap",
                    fontSize: 12,
                    color: "#166534",
                    background: "#dcfce7",
                    border: "1px solid #bbf7d0",
                    borderRadius: 999,
                    padding: "3px 8px",
                    fontWeight: 700,
                  }}
                >
                  {Number(s.score).toFixed(3)}
                </span>
              )}
            </div>

            {s.chunk_id && (
              <div
                style={{
                  marginTop: 8,
                  display: "inline-block",
                  fontSize: 12,
                  color: "#475569",
                  background: "#eef2ff",
                  border: "1px solid #e0e7ff",
                  borderRadius: 999,
                  padding: "3px 8px",
                  fontFamily:
                    "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                }}
              >
                {s.chunk_id}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}