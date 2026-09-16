import React from "react";

export interface ApprovalItem {
  requestId: string;
  taskId: string;
  capability: string;
  reason: string;
  riskLevel: "safe" | "moderate" | "destructive";
  timestamp: string;
}

interface ApprovalCenterProps {
  approvals: ApprovalItem[];
  onDecision: (requestId: string, approved: boolean) => void;
  onClose?: () => void;
}

export function ApprovalCenter({ approvals, onDecision, onClose }: ApprovalCenterProps) {
  if (approvals.length === 0) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 24,
        right: 24,
        zIndex: 9999,
        width: 380,
        backgroundColor: "#16161c",
        border: "1px solid #dc2626",
        borderRadius: 8,
        boxShadow: "0 8px 30px rgba(0,0,0,0.8)",
        overflow: "hidden",
        fontFamily: "'JetBrains Mono', monospace",
      }}
    >
      <div
        style={{
          padding: "10px 14px",
          backgroundColor: "rgba(220, 38, 38, 0.2)",
          borderBottom: "1px solid #dc2626",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span style={{ fontSize: 12, fontWeight: 700, color: "#f87171" }}>
          ⚠️ GÜVENLİK VE ONAY MERKEZİ ({approvals.length})
        </span>
        {onClose && (
          <button
            onClick={onClose}
            style={{ background: "none", border: "none", color: "#9ca3af", cursor: "pointer" }}
          >
            ✕
          </button>
        )}
      </div>

      <div style={{ maxHeight: 400, overflowY: "auto", padding: 12 }}>
        {approvals.map((app) => (
          <div
            key={app.requestId}
            style={{
              padding: 12,
              marginBottom: 10,
              backgroundColor: "#1f1f27",
              borderRadius: 6,
              border: "1px solid #374151",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
              <span
                style={{
                  fontSize: 11,
                  fontWeight: 600,
                  color: app.riskLevel === "destructive" ? "#ef4444" : "#f59e0b",
                  textTransform: "uppercase",
                }}
              >
                [{app.riskLevel}] {app.capability}
              </span>
            </div>

            <div style={{ fontSize: 12, color: "#d1d5db", marginBottom: 8 }}>
              {app.reason}
            </div>

            <div style={{ fontSize: 10, color: "#6b7280", marginBottom: 10 }}>
              Görev ID: {app.taskId.slice(0, 8)}
            </div>

            <div style={{ display: "flex", gap: 8 }}>
              <button
                onClick={() => onDecision(app.requestId, true)}
                style={{
                  flex: 1,
                  padding: "6px 0",
                  backgroundColor: "#15803d",
                  color: "#fff",
                  border: "none",
                  borderRadius: 4,
                  fontSize: 11,
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                ONAYLA
              </button>
              <button
                onClick={() => onDecision(app.requestId, false)}
                style={{
                  flex: 1,
                  padding: "6px 0",
                  backgroundColor: "#b91c1c",
                  color: "#fff",
                  border: "none",
                  borderRadius: 4,
                  fontSize: 11,
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                REDDET
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
