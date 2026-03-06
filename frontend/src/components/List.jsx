import React, { useState } from "react";
import { useAuthStore } from "../store/useAuthStore";
import AuthModal from "./AuthModal";

const COLOR_CLASSES = [
  "bg-primary/15 text-primary",
  "bg-secondary/15 text-secondary",
  "bg-accent/15 text-accent",
  "bg-info/15 text-info",
  "bg-success/15 text-success",
  "bg-warning/15 text-warning",
  "bg-error/15 text-error",
];

const getInitials = (text = "") => {
  const parts = text.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "♪";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
};

const getColorClass = (seed = "") => {
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash * 31 + seed.charCodeAt(i)) % COLOR_CLASSES.length;
  }
  return COLOR_CLASSES[hash] || COLOR_CLASSES[0];
};

const List = ({ result, prompt = "" }) => {
  if (!result || !result.tracks?.length) {
    return null;
  }

  const { token, savePlaylist } = useAuthStore();
  const [authOpen, setAuthOpen] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState("");

  const handleSave = async () => {
    if (!token) {
      setAuthOpen(true);
      return;
    }
    setSaving(true);
    setSaveError("");
    try {
      await savePlaylist(
        result.playlist_id,
        prompt, // prompt IS the playlist name
        prompt,
      );
      setSaved(true);
    } catch (err) {
      setSaveError(err.message);
    } finally {
      setSaving(false);
    }
  };

  // After auth succeeds, retry save automatically
  const handleAuthSuccess = () => {
    setAuthOpen(false);
    handleSave();
  };

  const handleYouTubeExport = () => {
    const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    const youtubeUrl = `${baseUrl}/youtube/start?playlist_id=${result.playlist_id}`;
    window.open(youtubeUrl, "_blank");
  };

  return (
    <div className="space-y-4">
      <AuthModal
        isOpen={authOpen}
        onClose={() => setAuthOpen(false)}
        onSuccess={handleAuthSuccess}
      />

      <div className="flex items-center justify-between flex-wrap gap-2">
        <h2 className="text-2xl font-semibold">
          {result.playlist_name || "Generated Playlist"}
        </h2>
        <div className="flex items-center gap-2">
          {/* Save to Profile */}
          <button
            onClick={handleSave}
            disabled={saving || saved}
            className={`btn btn-sm gap-2 ${saved ? "btn-success" : "btn-outline"}`}
          >
            {saving ? (
              <span className="loading loading-spinner loading-xs" />
            ) : saved ? (
              <>✓ Saved</>
            ) : (
              <>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  className="w-4 h-4"
                >
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                  <polyline points="17 21 17 13 7 13 7 21" />
                  <polyline points="7 3 7 8 15 8" />
                </svg>
                Save to My Profile
              </>
            )}
          </button>

          {/* YouTube export */}
          <button
            onClick={handleYouTubeExport}
            className="btn btn-error btn-sm gap-2"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
            </svg>
            Open with Youtube
          </button>
        </div>
      </div>

      {saveError && (
        <div className="rounded-lg bg-error/10 border border-error/30 px-4 py-2 text-sm text-error">
          {saveError}
        </div>
      )}

      <ul className="divide-y divide-base-200 rounded-xl border border-base-200 bg-base-100">
        {result.tracks.map((track, index) => (
          <li
            key={index}
            className="flex items-center justify-between px-4 py-3 hover:bg-base-200/40"
          >
            <div className="flex items-center gap-4">
              {/* Profil Yuvarlağı */}
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${getColorClass(
                  `${track.artist_name}-${track.track_name}`,
                )}`}
              >
                {getInitials(track.track_name || track.artist_name)}
              </div>

              {/* Şarkı ve Sanatçı İsmi */}
              <div className="flex flex-col">
                <span className="font-medium text-base-content">
                  {track.track_name} {/* DEĞİŞİKLİK BURADA */}
                </span>
                <span className="text-sm text-base-content/60">
                  {track.artist_name} {/* DEĞİŞİKLİK BURADA */}
                </span>
              </div>
            </div>
            <span className="text-xs text-base-content/40 font-mono">
              #{index + 1}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default List;
