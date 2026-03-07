import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../store/useAuthStore";

// ── Track detail modal ────────────────────────────────────────────────────────
const PlaylistDetailModal = ({ playlist, onClose }) => {
  const { restoreForYoutube } = useAuthStore();
  const [ytLoading, setYtLoading] = useState(false);

  if (!playlist) return null;

  const handleYouTube = async () => {
    setYtLoading(true);
    try {
      const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const tempId = await restoreForYoutube(playlist.id);
      window.open(`${baseUrl}/youtube/start?playlist_id=${tempId}`, "_blank");
    } catch (e) {
      alert("YouTube export failed: " + e.message);
    } finally {
      setYtLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4"
      onClick={onClose}
    >
      <div
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
          <button
            onClick={onClose}
            className="btn btn-ghost btn-sm btn-circle shrink-0"
          >
            ✕
          </button>
        </div>

        {/* Track list */}
        <ul className="divide-y divide-base-200 rounded-xl border border-base-200 overflow-y-auto flex-1">
          {playlist.tracks.map((track, i) => (
            <li
              key={i}
              className="flex items-center gap-3 px-4 py-2.5 hover:bg-base-200/40"
            >
              <span className="text-xs text-base-content/40 font-mono w-5 shrink-0">
                {i + 1}
              </span>
              <div className="flex flex-col min-w-0">
                <span className="font-medium truncate">{track.track_name}</span>
                <span className="text-sm text-base-content/60 truncate">
                  {track.artist_name}
                </span>
              </div>
            </li>
          ))}
        </ul>

        {/* YouTube button */}
        <button
          onClick={handleYouTube}
          disabled={ytLoading}
          className="btn btn-error w-full gap-2"
        >
          {ytLoading ? (
            <span className="loading loading-spinner loading-sm" />
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="w-5 h-5"
            >
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
            </svg>
          )}
          Open with YouTube
        </button>
      </div>
    </div>
  );
};

// ── My Playlists page ─────────────────────────────────────────────────────────
const MyPlaylists = () => {
  const { token, user, fetchMyPlaylists, logout } = useAuthStore();
  const [playlists, setPlaylists] = useState([]);
  // Lazy initializer: start in "loading" only if we already have a token
  const [loading, setLoading] = useState(() => !!token);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    if (!token) return;
    fetchMyPlaylists()
      .then(setPlaylists)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token, fetchMyPlaylists]);

  // ── Not logged in ──────────────────────────────────────────────────────────
  if (!token) {
    return (
      <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-6">
        <div className="text-center space-y-4">
          <p className="text-lg font-medium">
            Sign in to see your saved playlists.
          </p>
          <Link to="/" className="btn btn-primary">
            ← Go to home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-8rem)] bg-gradient-to-br from-base-200 to-base-300 px-6 py-12">
      <PlaylistDetailModal
        playlist={selected}
        onClose={() => setSelected(null)}
      />

      <div className="mx-auto max-w-4xl space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold">My Playlists</h1>
            <p className="text-base-content/60 text-sm mt-1">{user?.email}</p>
          </div>
          <div className="flex gap-2">
            <Link to="/" className="btn btn-ghost btn-sm">
              ← Generate New
            </Link>
            <button onClick={logout} className="btn btn-outline btn-sm">
              Sign out
            </button>
          </div>
        </div>

        {/* States */}
        {loading && (
          <div className="flex justify-center py-20">
            <span className="loading loading-spinner loading-lg text-primary" />
          </div>
        )}

        {error && (
          <div className="rounded-lg bg-error/10 border border-error/30 px-4 py-3 text-error">
            {error}
          </div>
        )}

        {!loading && !error && playlists.length === 0 && (
          <div className="text-center py-20 space-y-3">
            <p className="text-4xl">🎵</p>
            <p className="text-lg font-medium">No saved playlists yet.</p>
            <Link to="/" className="btn btn-primary btn-sm">
              Generate your first one
            </Link>
          </div>
        )}

        {/* Playlist grid */}
        {!loading && playlists.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {playlists.map((pl) => (
              <button
                key={pl.id}
                onClick={() => setSelected(pl)}
                className="text-left rounded-2xl border border-base-200 bg-base-100 shadow hover:shadow-md hover:-translate-y-0.5 transition-all p-6 space-y-3 cursor-pointer"
              >
                {/* Icon */}
                <div className="w-10 h-10 rounded-full bg-primary/15 text-primary flex items-center justify-center text-lg font-bold shrink-0">
                  {pl.playlist_name.charAt(0).toUpperCase()}
                </div>

                <p className="font-semibold line-clamp-2 text-sm leading-snug">
                  {pl.playlist_name}
                </p>

                {pl.prompt && pl.prompt !== pl.playlist_name && (
                  <p className="text-xs text-base-content/50 italic line-clamp-2 leading-snug border-l-2 border-primary/30 pl-2">
                    "{pl.prompt}"
                  </p>
                )}

                <div className="flex items-center justify-between text-xs text-base-content/40">
                  <span>{pl.tracks.length} tracks</span>
                  <span>
                    {new Date(pl.created_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    })}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyPlaylists;
