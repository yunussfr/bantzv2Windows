import React, { useState, useEffect, useRef } from "react";
import { useWebSocket } from "../hooks/useWebSocket";

const WS_URL = "ws://localhost:8765";

export type AvatarState =
  | "idle"
  | "listening"
  | "voice_chat"
  | "thinking"
  | "working"
  | "success"
  | "error"
  | "waiting_for_user";

const STATE_COLORS: Record<AvatarState, string> = {
  idle: "#4a4a52",
  listening: "#e8b44a",
  voice_chat: "#38bdf8",
  thinking: "#d97742",
  working: "#a855f7",
  success: "#22c55e",
  error: "#ef4444",
  waiting_for_user: "#f59e0b",
};

export function AvatarOverlay() {
  const [avatarState, setAvatarState] = useState<AvatarState>("idle");
  const [speechText, setSpeechText] = useState("");
  const [avatarUrl, setAvatarUrl] = useState<string | null>(() => {
    return localStorage.getItem("bantz_avatar_image") || null;
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { status, send } = useWebSocket({
    url: WS_URL,
    reconnectDelay: 2000,
    onMessage: (msg) => {
      const d = msg.data as any;
      if (!d || typeof d !== "object") return;

      if (d.type === "avatar_state" || d.type === "voice_state") {
        const s = d.state as AvatarState;
        if (s && STATE_COLORS[s]) {
          setAvatarState(s);
        }
      } else if (d.type === "speech_bubble" || d.type === "voice_transcript") {
        setSpeechText(d.text || "");
      } else if (d.type === "motion_command") {
        // Güvenli görsel animasyon tetikleme
        handleMotion(d.command, d.parameters);
      }
    },
  });

  const handleMotion = (command: string, params: any) => {
    // bounce, shake, pulse vb. CSS animasyonlarını tetikle
    const el = document.getElementById("bantz-avatar-img");
    if (!el) return;
    if (command === "bounce") {
      el.style.animation = "avatar-bounce 0.5s ease 2";
    } else if (command === "shake") {
      el.style.animation = "avatar-shake 0.4s ease 2";
    } else if (command === "pulse") {
      el.style.animation = "avatar-pulse 0.8s ease 2";
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // PNG, WebP, GIF doğrulaması
    if (!["image/png", "image/webp", "image/gif"].includes(file.type)) {
      alert("Lütfen geçerli bir PNG, WebP veya GIF dosyası yükleyin.");
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      setAvatarUrl(result);
      localStorage.setItem("bantz_avatar_image", result);
    };
    reader.readAsDataURL(file);
  };

  const accentColor = STATE_COLORS[avatarState];

  return (
    <div
      data-tauri-drag-region
      style={{
        width: "100%",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-end",
        paddingBottom: 16,
        background: "transparent",
        userSelect: "none",
      }}
    >
      <style>{`
        @keyframes avatar-bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-16px); }
        }
        @keyframes avatar-shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-8px); }
          75% { transform: translateX(8px); }
        }
        @keyframes avatar-pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.08); }
        }
      `}</style>

      {/* Konuşma Balonu (Speech Bubble) */}
      {speechText && (
        <div
          style={{
            maxWidth: 240,
            padding: "8px 12px",
            marginBottom: 8,
            borderRadius: 8,
            backgroundColor: "rgba(20, 20, 24, 0.95)",
            border: `1px solid ${accentColor}`,
            color: "#f3f4f6",
            fontSize: 12,
            boxShadow: `0 4px 12px ${accentColor}33`,
            animation: "avatar-pulse 1s ease",
            wordBreak: "break-word",
          }}
        >
          {speechText}
        </div>
      )}

      {/* Avatar Container */}
      <div
        data-tauri-drag-region
        onClick={() => {
          if (!avatarUrl && fileInputRef.current) {
            fileInputRef.current.click();
          }
        }}
        style={{
          width: 96,
          height: 96,
          borderRadius: "50%",
          border: `2px solid ${accentColor}`,
          boxShadow: `0 0 16px ${accentColor}66`,
          backgroundColor: "#111116",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "grab",
          overflow: "hidden",
          position: "relative",
          transition: "border-color 0.3s, box-shadow 0.3s",
        }}
      >
        {avatarUrl ? (
          <img
            id="bantz-avatar-img"
            src={avatarUrl}
            alt="Avatar"
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <div style={{ color: "#71717a", fontSize: 10, textAlign: "center", padding: 4 }}>
            Avatar Yükle (Tıkla)
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/png, image/webp, image/gif"
        style={{ display: "none" }}
        onChange={handleFileUpload}
      />

      {/* Durum Etiketi */}
      <div
        style={{
          marginTop: 6,
          fontSize: 9,
          fontWeight: 700,
          letterSpacing: "0.15em",
          color: accentColor,
          backgroundColor: "rgba(10, 10, 14, 0.8)",
          padding: "2px 8px",
          borderRadius: 4,
        }}
      >
        {avatarState.toUpperCase()}
      </div>
    </div>
  );
}
