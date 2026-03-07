import React from "react";

export function Feedback({ requestId, onFeedback, feedbackState }) {
    return (
        <div style={{ marginTop: 14, padding: 14, borderRadius: 10, border: "1px solid #ddd" }}>
            <h3 style={{ marginTop: 0 }}>Was this helpful?</h3>
            <div style={{ display: "flex", gap: 10 }}>
                <button
                    onClick={() => onFeedback("up")}
                    disabled={!requestId || feedbackState !== null}
                    style={{ padding: "10px 14px", borderRadius: 10, border: "1px solid #222", cursor: "pointer" }}
                >
                    👍
                </button>
                <button
                    onClick={() => onFeedback("down")}
                    disabled={!requestId || feedbackState !== null}
                    style={{ padding: "10px 14px", borderRadius: 10, border: "1px solid #222", cursor: "pointer" }}
                >
                    👎
                </button>
                {feedbackState && <div style={{ alignSelf: "center", color: "#444" }}>Thanks for the feedback.</div>}
            </div>
        </div>
    );
}
