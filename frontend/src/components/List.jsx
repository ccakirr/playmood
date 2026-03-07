import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../store/useAuthStore";
import { useToast } from "./Toast";
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
  if (!result || !result.tracks?.length) return null;

  const { token, savePlaylist } = useAuthStore();
  const { addToast } = useToast();
  const [authOpen, setAuthOpen] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!token) {
      setAuthOpen(true);
      return;
    }
    setSaving(true);
    try {
      await savePlaylist(result.playlist_id, prompt, prompt);
      setSaved(true);
      addToast({ message: "Playlist saved to your profile!", type: "success" });
    } catch (err) {
      addToast({ message: err.message || "Save failed.", type: "error" });
    } finally {
      setSaving(false);
    }
  };

  const handleAuthSuccess = () => {
    setAuthOpen(false);
    handleSave();
  };

  const handleYouTubeExport = () => {
    const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    window.open(`${baseUrl}/youtube/start?playlist_id=${result.playlist_id}`, "_blank");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-4"
    >
      <AuthModal
        isOpen={authOpen}
        onClose={() => setAuthOpen(false)}
        onSuccess={handleAuthSuccess}
      />

      {/* Header row */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h2 className="text-2xl font-semibold">
          {result.playlist_name || "Generated Playlist"}
        </h2>
        <div className="flex items-center gap-2">
          {/* Save button */}
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={handleSave}
            disabled={saving || saved}
            className={`btn btn-sm gap-2 ${saved ? "btn-success" : "btn-outline"}`}
          >
            <AnimatePresence mode="wait" initial={false}>
              {saving ? (
                <motion.span key="spin" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <span className="loading loading-spinner loading-xs" />
                </motion.span>
              ) : saved ? (
                <motion.span key="saved" initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }} className="flex items-center gap-1">
                  ✓ Saved
                </motion.span>
              ) : (
                <motion.span key="save" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex items-center gap-1.5">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                    <polyline points="17 21 17 13 7 13 7 21" />
                    <polyline points="7 3 7 8 15 8" />
                  </svg>
                  Save to My Profile
                </motion.span>
              )}
            </AnimatePresence>
          </motion.button>

          {/* YouTube button */}
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={handleYouTubeExport}
            className="btn btn-error btn-sm gap-2"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
            </svg>
            Open with YouTube
          </motion.button>
        </div>
      </div>

      {/* Track table */}
      <div className="rounded-xl border border-base-200 bg-base-100 overflow-hidden">
        {/* Table header */}
        <div className="grid grid-cols-[2rem_1fr_auto] gap-4 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-base-content/40 border-b border-base-200">
          <span className="text-center">#</span>
          <span>Track / Artist</span>
          <span></span>
        </div>

        {/* Rows */}
        <ul>
          {result.tracks.map((track, index) => (
            <motion.li
              key={index}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.03, duration: 0.25 }}
              className="group grid grid-cols-[2rem_1fr_auto] items-center gap-4 px-4 py-3 hover:bg-base-200/50 transition-colors duration-150 border-b border-base-200/50 last:border-0"
            >
              {/* Index */}
              <span className="text-xs text-base-content/40 font-mono text-center tabular-nums">
                {index + 1}
              </span>

              {/* Avatar + Track info */}
              <div className="flex items-center gap-3 min-w-0">
                <div
                  className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-xs font-bold ${getColorClass(
                    `${track.artist_name}-${track.track_name}`,
                  )}`}
                >
                  {getInitials(track.track_name || track.artist_name)}
                </div>
                <div className="min-w-0">
                  <p className="font-medium truncate leading-tight">
                    {track.track_name}
                  </p>
                  <p className="text-sm text-base-content/55 truncate">
                    {track.artist_name}
                  </p>
                </div>
              </div>

              {/* YouTube icon — visible on hover */}
              <motion.a
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                href={`https://www.youtube.com/results?search_query=${encodeURIComponent(track.query || `${track.track_name} ${track.artist_name}`)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="opacity-0 group-hover:opacity-70 hover:!opacity-100 transition-opacity text-error"
                aria-label={`Open ${track.track_name} on YouTube`}
                title="Open on YouTube"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                </svg>
              </motion.a>
            </motion.li>
          ))}
        </ul>
      </div>
    </motion.div>
  );
};

export default List;

