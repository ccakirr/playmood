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

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">{result.playlist_name}</h2>
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
