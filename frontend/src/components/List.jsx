import React from "react";

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

const List = ({ result }) => {
  if (!result || !result.tracks?.length) {
    return null;
  }

  const handleYouTubeExport = () => {
    const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    const youtubeUrl = `${baseUrl}/youtube/start?playlist_id=${result.playlist_id}`;
    window.open(youtubeUrl, "_blank");
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">{result.playlist_name}</h2>
        <button
          onClick={handleYouTubeExport}
          className="btn btn-error btn-sm gap-2"
          title="Open it from Youtube"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="w-5 h-5"
          >
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
          </svg>
          YouTube'da Aç
        </button>
      </div>

      {/* Info Alert */}
      <div className="alert alert-info">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          className="stroke-current shrink-0 w-6 h-6"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          ></path>
        </svg>
        <div className="text-sm">
          <p>
            <strong>First time using YouTube?</strong> You'll see a Google
            security warning. Click "Advanced" → "Go to PlayMood" to continue
            safely.
          </p>
        </div>
      </div>

      <ul className="divide-y divide-base-200 rounded-xl border border-base-200">
        {result.tracks.map((track, index) => (
          <li
            key={`${track.artist}-${track.title}-${index}`}
            className="flex items-center justify-between px-4 py-3 hover:bg-base-200/40"
          >
            <div className="flex items-center gap-3">
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-full text-xs font-semibold ${getColorClass(
                  `${track.artist}-${track.title}`,
                )}`}
                aria-hidden="true"
              >
                {getInitials(track.title || track.artist)}
              </div>
              <p className="font-medium">{track.title}</p>
              <p className="text-sm text-base-content/60">{track.artist}</p>
            </div>
            <span className="text-xs text-base-content/40">#{index + 1}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default List;
