import React from "react";

export function SourceList({ sources }) {
    if (!sources || sources.length === 0) {
        return (
            <div style={{ marginTop: 14, padding: 14, borderRadius: 10, border: "1px solid #ddd" }}>
                <h3 style={{ marginTop: 0 }}>Sources used</h3>
                <div style={{ color: "#666" }}>No sources returned (unsafe flow or retrieval returned none).</div>
            </div>
        );
    }

    return (
        <div style={{ marginTop: 14, padding: 14, borderRadius: 10, border: "1px solid #ddd" }}>
            <h3 style={{ marginTop: 0 }}>Sources used</h3>
            <ol style={{ margin: 0, paddingLeft: 18 }}>
                {sources.map((s) => (
                    <li key={s.chunk_id || Math.random()} style={{ marginBottom: 10 }}>
                        <div><strong>{s.title || "Untitled"}</strong></div>
                        <div style={{ color: "#555" }}>
                            Chunk: {s.chunk_id} • Score: {Number(s.score).toFixed(3)}
                        </div>
                        {s.source && <div style={{ color: "#777" }}>Source: {s.source}</div>}
                    </li>
                ))}
            </ol>
        </div>
    );
}
