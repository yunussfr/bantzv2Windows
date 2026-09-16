import React from "react";

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  level: "info" | "warning" | "error" | "success";
  timestamp: string;
}

interface NotificationCenterProps {
  notifications: NotificationItem[];
  onDismiss: (id: string) => void;
}

export function NotificationCenter({ notifications, onDismiss }: NotificationCenterProps) {
  if (notifications.length === 0) return null;

  return (
    <div
      style={{
        position: "fixed",
        bottom: 24,
        right: 24,
        zIndex: 9998,
        display: "flex",
        flexDirection: "column",
        gap: 8,
        maxWidth: 360,
        fontFamily: "'JetBrains Mono', monospace",
      }}
    >
      {notifications.map((n) => {
        const borderColors = {
          info: "#38bdf8",
          warning: "#f59e0b",
          error: "#ef4444",
          success: "#22c55e",
        };
        return (
          <div
            key={n.id}
            style={{
              padding: "10px 14px",
              backgroundColor: "#16161c",
              border: `1px solid ${borderColors[n.level]}`,
              borderRadius: 6,
              boxShadow: "0 4px 14px rgba(0,0,0,0.5)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
            }}
          >
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: borderColors[n.level], marginBottom: 2 }}>
                {n.title}
              </div>
              <div style={{ fontSize: 11, color: "#e5e7eb" }}>{n.message}</div>
            </div>
            <button
              onClick={() => onDismiss(n.id)}
              style={{
                background: "none",
                border: "none",
                color: "#9ca3af",
                cursor: "pointer",
                padding: "0 4px",
                fontSize: 12,
              }}
            >
              ✕
            </button>
          </div>
        );
      })}
    </div>
  );
}
