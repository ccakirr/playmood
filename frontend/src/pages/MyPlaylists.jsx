import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion as Motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../store/useAuthStore";
import { useToast } from "../components/Toast";

// ── Mood → accent color mapping ───────────────────────────────────────────────
const MOOD_COLORS = [
  "from-primary/20 to-primary/5 border-primary/20 text-primary",
  "from-secondary/20 to-secondary/5 border-secondary/20 text-secondary",
  "from-accent/20 to-accent/5 border-accent/20 text-accent",
  "from-info/20 to-info/5 border-info/20 text-info",
  "from-success/20 to-success/5 border-success/20 text-success",
  "from-warning/20 to-warning/5 border-warning/20 text-warning",
  "from-error/20 to-error/5 border-error/20 text-error",
];

const getMoodColor = (seed = "") => {
  let h = 0;
  for (let i = 0; i < seed.length; i++)
    h = (h * 31 + seed.charCodeAt(i)) % MOOD_COLORS.length;
  return MOOD_COLORS[h];
};

// ── Skeleton card ─────────────────────────────────────────────────────────────
const SkeletonCard = () => (
  <div className="rounded-2xl border border-base-200 bg-base-100 p-5 space-y-3 animate-pulse">
    <div className="w-10 h-10 rounded-full bg-base-300" />
    <div className="h-3.5 w-3/4 rounded bg-base-300" />
    <div className="h-3 w-1/2 rounded bg-base-300" />
    <div className="flex justify-between">
      <div className="h-3 w-16 rounded bg-base-300" />
      <div className="h-3 w-20 rounded bg-base-300" />
    </div>
  </div>
);

// ── Empty state ───────────────────────────────────────────────────────────────
const EmptyState = ({ notLoggedIn }) => (
  <Motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="flex flex-col items-center justify-center py-24 gap-6"
  >
    {/* SVG illustration */}
    <svg
      className="w-32 h-32 text-base-content/10"
      fill="none"
      viewBox="0 0 120 120"
    >
      <circle
        cx="60"
        cy="60"
        r="56"
        stroke="currentColor"
        strokeWidth="3"
        strokeDasharray="8 6"
      />
      <path
        d="M44 52c0-8.837 7.163-16 16-16s16 7.163 16 16v18a4 4 0 01-8 0V52a8 8 0 00-16 0v18a4 4 0 01-8 0V52z"
        fill="currentColor"
        opacity=".4"
      />
      <circle cx="48" cy="74" r="6" fill="currentColor" opacity=".5" />
      <circle cx="72" cy="74" r="6" fill="currentColor" opacity=".5" />
    </svg>

    {notLoggedIn ? (
      <>
        <div className="text-center space-y-1">
          <p className="text-xl font-semibold">Sign in to see your playlists</p>
          <p className="text-sm text-base-content/50">
            Your saved playlists will appear here
          </p>
        </div>
        <Link to="/" className="btn btn-primary btn-sm px-6">
          ← Go to home
        </Link>
      </>
    ) : (
      <>
        <div className="text-center space-y-1">
          <p className="text-xl font-semibold">No playlists yet</p>
          <p className="text-sm text-base-content/50">
            Generate your first playlist and hit Save
          </p>
        </div>
        <Link to="/" className="btn btn-primary btn-sm px-6">
          Generate one now
        </Link>
      </>
    )}
  </Motion.div>
);

// ── Detail modal ──────────────────────────────────────────────────────────────
const PlaylistDetailModal = ({ playlist, onClose, onDelete }) => {
  const { restoreForYoutube } = useAuthStore();
  const { addToast } = useToast();
  const [ytLoading, setYtLoading] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  if (!playlist) return null;

  const handleYouTube = async () => {
    setYtLoading(true);
    // Open window synchronously inside the user-gesture handler so mobile
    // browsers (iOS Safari etc.) don't block it as a popup.
    const newWindow = window.open("", "_blank");
    try {
      const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const tempId = await restoreForYoutube(playlist.id);
      if (newWindow) {
        newWindow.location.href = `${baseUrl}/youtube/start?playlist_id=${tempId}`;
      }
    } catch (e) {
      if (newWindow) newWindow.close();
      addToast({
        message: "YouTube export failed: " + e.message,
        type: "error",
      });
    } finally {
      setYtLoading(false);
    }
  };

  return (
    <AnimatePresence>
      <Motion.div
        key="backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4"
        onClick={onClose}
      >
        <Motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: "spring", stiffness: 350, damping: 28 }}
          className="w-full max-w-lg rounded-2xl border border-base-200 bg-base-100 shadow-2xl p-8 space-y-4 max-h-[85vh] flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <h3 className="text-xl font-bold line-clamp-2">
                {playlist.playlist_name}
              </h3>
              <p className="text-xs text-base-content/40 mt-1">
                {new Date(playlist.created_at).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
                {" · "}
                {playlist.tracks.length} tracks
              </p>
            </div>
            <div className="flex items-center gap-1 shrink-0">
              {confirmDelete ? (
                <>
                  <button
                    onClick={() => onDelete(playlist.id)}
                    className="btn btn-error btn-sm gap-1"
                  >
                    Confirm Delete
                  </button>
                  <button
                    onClick={() => setConfirmDelete(false)}
                    className="btn btn-ghost btn-sm"
                  >
                    Cancel
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setConfirmDelete(true)}
                  className="btn btn-ghost btn-sm btn-circle text-error/60 hover:text-error hover:bg-error/10"
                  title="Delete playlist"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              )}
              <button
                onClick={onClose}
                className="btn btn-ghost btn-sm btn-circle"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Track list */}
          <ul className="divide-y divide-base-200 rounded-xl border border-base-200 overflow-y-auto flex-1">
            {playlist.tracks.map((track, i) => (
              <li
                key={i}
                className="flex items-center gap-3 px-4 py-2.5 hover:bg-base-200/40 transition-colors"
              >
                <span className="text-xs text-base-content/40 font-mono w-5 shrink-0 tabular-nums">
                  {i + 1}
                </span>
                <div className="flex flex-col min-w-0">
                  <span className="font-medium truncate">
                    {track.track_name}
                  </span>
                  <span className="text-sm text-base-content/60 truncate">
                    {track.artist_name}
                  </span>
                </div>
              </li>
            ))}
          </ul>

          {/* YouTube */}
          <Motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleYouTube}
            disabled={ytLoading}
            className="btn btn-error w-full gap-2"
          >
            {ytLoading ? (
              <span className="loading loading-spinner loading-sm" />
            ) : (
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
              </svg>
            )}
            Open with YouTube
          </Motion.button>
        </Motion.div>
      </Motion.div>
    </AnimatePresence>
  );
};

// ── Bento playlist card ───────────────────────────────────────────────────────
const PlaylistCard = ({ pl, index, onClick, onDelete }) => {
  const [hovered, setHovered] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const colorClass = getMoodColor(pl.playlist_name);
  const previewArtists = [
    ...new Set(pl.tracks.slice(0, 4).map((t) => t.artist_name)),
  ].slice(0, 3);

  const handleDeleteClick = (e) => {
    e.stopPropagation();
    if (confirmDelete) {
      onDelete(pl.id);
    } else {
      setConfirmDelete(true);
    }
  };

  return (
    <Motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      whileHover={{ y: -4, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      onHoverStart={() => { setHovered(true); }}
      onHoverEnd={() => { setHovered(false); setConfirmDelete(false); }}
      className={`relative text-left rounded-2xl border bg-gradient-to-br ${colorClass} shadow hover:shadow-lg transition-shadow duration-200 p-5 space-y-3 cursor-pointer overflow-hidden w-full`}
    >
      {/* Glassmorphism glow blob */}
      <div className="absolute -top-6 -right-6 w-24 h-24 rounded-full bg-current opacity-5 blur-2xl pointer-events-none" />

      {/* Icon */}
      <div
        className={`w-10 h-10 rounded-xl bg-current/10 border border-current/20 flex items-center justify-center text-base font-bold`}
      >
        {pl.playlist_name.charAt(0).toUpperCase()}
      </div>

      <p className="font-semibold line-clamp-2 text-sm leading-snug text-base-content">
        {pl.playlist_name}
      </p>

      {/* Quick-view: artist names on hover */}
      <AnimatePresence mode="wait">
        {hovered && previewArtists.length > 0 ? (
          <Motion.div
            key="artists"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="space-y-0.5 pt-1 border-t border-current/10">
              {previewArtists.map((a, i) => (
                <p
                  key={i}
                  className="text-xs text-base-content/60 truncate flex items-center gap-1"
                >
                  <span className="w-1 h-1 rounded-full bg-current/50 shrink-0" />
                  {a}
                </p>
              ))}
            </div>
          </Motion.div>
        ) : pl.prompt && pl.prompt !== pl.playlist_name ? (
          <Motion.p
            key="prompt"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-xs text-base-content/50 italic line-clamp-2 leading-snug border-l-2 border-current/30 pl-2"
          >
            "{pl.prompt}"
          </Motion.p>
        ) : (
          <Motion.span key="empty" />
        )}
      </AnimatePresence>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-base-content/40 pt-1">
        <span className="font-medium">{pl.tracks.length} tracks</span>
        <div className="flex items-center gap-2">
          <span>
            {new Date(pl.created_at).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "numeric",
            })}
          </span>
          {hovered && (
            <button
              onClick={handleDeleteClick}
              className={`btn btn-xs gap-1 transition-colors ${
                confirmDelete
                  ? "btn-error"
                  : "btn-ghost opacity-60 hover:opacity-100"
              }`}
            >
              {confirmDelete ? (
                "Delete?"
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-3.5 h-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              )}
            </button>
          )}
        </div>
      </div>
    </Motion.div>
  );
};

// ── Page ──────────────────────────────────────────────────────────────────────
const MyPlaylists = () => {
  const { token, user, fetchMyPlaylists, deletePlaylist } = useAuthStore();
  const { addToast } = useToast();
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(() => !!token);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);

  const handleDelete = async (id) => {
    try {
      await deletePlaylist(id);
      setPlaylists((prev) => prev.filter((p) => p.id !== id));
      setSelected(null);
      addToast({ message: "Playlist deleted.", type: "success" });
    } catch (e) {
      addToast({ message: "Delete failed: " + e.message, type: "error" });
    }
  };

  useEffect(() => {
    if (!token) return;
    fetchMyPlaylists()
      .then(setPlaylists)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token, fetchMyPlaylists]);

  if (!token) {
    return <EmptyState notLoggedIn />;
  }

  return (
    <div className="min-h-[calc(100vh-8rem)] bg-gradient-to-br from-base-200 to-base-300 px-6 py-12">
      <AnimatePresence>
        {selected && (
          <PlaylistDetailModal
            playlist={selected}
            onClose={() => setSelected(null)}
            onDelete={handleDelete}
          />
        )}
      </AnimatePresence>

      <div className="mx-auto max-w-5xl space-y-8">
        {/* Page header */}
        <Motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between flex-wrap gap-4"
        >
          <div>
            <h1 className="text-3xl font-bold">My Playlists</h1>
            <p className="text-base-content/50 text-sm mt-0.5">{user?.email}</p>
          </div>
          <Link to="/" className="btn btn-ghost btn-sm gap-1">
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 4v16m8-8H4"
              />
            </svg>
            Generate New
          </Link>
        </Motion.div>

        {/* Error */}
        {error && (
          <div className="rounded-xl bg-error/10 border border-error/30 px-4 py-3 text-sm text-error">
            {error}
          </div>
        )}

        {/* Skeleton */}
        {loading && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}

        {/* Empty */}
        {!loading && !error && playlists.length === 0 && <EmptyState />}

        {/* Bento grid */}
        {!loading && playlists.length > 0 && (
          <Motion.div
            layout
            className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
          >
            {playlists.map((pl, i) => (
              <PlaylistCard
                key={pl.id}
                pl={pl}
                index={i}
                onClick={() => setSelected(pl)}
                onDelete={handleDelete}
              />
            ))}
          </Motion.div>
        )}
      </div>
    </div>
  );
};

export default MyPlaylists;
